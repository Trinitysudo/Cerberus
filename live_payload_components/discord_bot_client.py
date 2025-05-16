# F:/Cerebus/live_payload_components/discord_bot_client.py

import discord
import asyncio
import threading
import traceback

_builder_client = None
_builder_loop = None
_builder_thread = None
_builder_ready_event = threading.Event() # Signals when client.login() has completed AND on_ready has fired.

def _start_builder_bot_loop(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass # Allow clean interruption
    finally:
        print("[Builder Bot] Event loop stopped.")
        # Ensure all pending tasks are cancelled before closing loop
        # This is important for graceful shutdown
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        # Allow tasks to be cancelled
        # loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True)) 
        # The above line can cause issues if loop is already stopping/closed.
        # A simpler approach for cleanup is just to close.
        loop.close()
        print("[Builder Bot] Event loop closed.")


async def _builder_login_and_run_minimal(token):
    """Logs in and briefly connects to ensure on_ready fires, then idles."""
    global _builder_client, _builder_ready_event, _builder_loop

    intents = discord.Intents.default()
    # If you only send messages and don't need to read message content,
    # you might not need intents.messages = True for the SENDER.
    # intents.messages = True # Enable if needed for specific operations or due to Discord changes
    
    _builder_client = discord.Client(loop=_builder_loop, intents=intents)

    @_builder_client.event
    async def on_ready():
        # This event is crucial. It means the bot is fully connected and caches are populated.
        print(f"[Builder Bot] ON_READY: Logged in as {_builder_client.user} (ID: {_builder_client.user.id})")
        print("[Builder Bot] Client is fully ready.")
        _builder_ready_event.set() # Signal that the bot is fully operational

    try:
        # Using client.start() and then quickly client.close() after on_ready
        # is a more robust way to ensure the client is truly ready for send operations
        # than just client.login().
        # We'll start it, wait for on_ready, then it will idle until shutdown.
        await _builder_client.start(token) # This will run until client.close() is called
    except discord.LoginFailure:
        print("[Builder Bot] Login failed. Please check the Bot Token.")
        _builder_ready_event.set() # Set event to release wait, error handled by caller
    except KeyboardInterrupt:
        print("[Builder Bot] Bot startup interrupted.")
        if _builder_client and not _builder_client.is_closed():
            await _builder_client.close()
        _builder_ready_event.set()
    except Exception as e:
        print(f"[Builder Bot] Error during bot login/startup: {e}")
        _builder_ready_event.set() # Release wait
    finally:
        if _builder_client and not _builder_client.is_closed():
            print("[Builder Bot] Ensuring client is closed in _builder_login_and_run_minimal finally block.")
            # await _builder_client.close() # client.start() handles its own cleanup on loop stop
        print("[Builder Bot] _builder_login_and_run_minimal task finished.")


def initialize_builder_discord_sender(bot_token):
    global _builder_client, _builder_loop, _builder_thread, _builder_ready_event

    if _builder_thread and _builder_thread.is_alive():
        print("[Builder Bot] Client thread already running.")
        if _builder_ready_event.is_set() and _builder_client and _builder_client.is_ready():
            return True
        print("[Builder Bot] Thread running, but client not ready. Waiting for ready event...")
        return _builder_ready_event.wait(timeout=15)

    _builder_ready_event.clear()
    _builder_loop = asyncio.new_event_loop()
    
    _builder_thread = threading.Thread(target=_start_builder_bot_loop, args=(_builder_loop,), daemon=True)
    _builder_thread.name = "BuilderDiscordSendThread"
    _builder_thread.start()

    # Schedule the login and minimal run task
    asyncio.run_coroutine_threadsafe(_builder_login_and_run_minimal(bot_token), _builder_loop)

    print("[Builder Bot] Waiting for Discord client to be fully ready (on_ready event)...")
    if _builder_ready_event.wait(timeout=25): # Wait up to 25 seconds for on_ready
        if _builder_client and _builder_client.is_ready() and _builder_client.user:
            print(f"[Builder Bot] Client initialization successful and fully ready. Logged in as {_builder_client.user}.")
            return True
        else:
            print("[Builder Bot] on_ready event received, but client state is not as expected (not ready or no user).")
            return False
    else:
        print("[Builder Bot] Client initialization timed out waiting for on_ready signal.")
        return False

async def _send_message_async_for_builder(channel_id: int, message_content: str):
    global _builder_client
    if not (_builder_client and _builder_client.is_ready()):
        print("[Builder Bot] Client not initialized or not ready for sending.")
        return False
    # No need for wait_until_ready here if initialize_builder_discord_sender ensures it via on_ready

    try:
        # Attempt to get channel from cache first
        channel = _builder_client.get_channel(channel_id)
        if not channel:
            print(f"[Builder Bot] Channel {channel_id} not in cache, attempting to fetch...")
            try:
                channel = await _builder_client.fetch_channel(channel_id)
            except discord.NotFound:
                print(f"[Builder Bot] Channel {channel_id} not found after fetch.")
                return False
            except discord.Forbidden:
                print(f"[Builder Bot] Bot lacks permission to fetch channel {channel_id}.")
                return False
            except Exception as e_fetch:
                print(f"[Builder Bot] Error fetching channel {channel_id}: {e_fetch}")
                return False
        
        if channel:
            await channel.send(message_content)
            print(f"[Builder Bot] Message successfully sent to channel {channel_id}.")
            return True
        else: # Should be caught by fetch logic if initial get_channel failed
            print(f"[Builder Bot] Channel {channel_id} could not be resolved for sending.")
            return False
            
    except discord.Forbidden:
        print(f"[Builder Bot] Bot lacks permissions to send to channel {channel_id}.")
        return False
    except discord.HTTPException as e:
        print(f"[Builder Bot] Failed to send message due to HTTP Exception: {e.status} - {e.text}")
        return False
    except Exception as e:
        print(f"[Builder Bot] An unexpected error occurred while sending message: {e}")
        traceback.print_exc()
        return False

def send_command_from_builder(channel_id_str: str, message_content: str):
    global _builder_loop, _builder_thread, _builder_client, _builder_ready_event

    if not (_builder_loop and _builder_thread and _builder_thread.is_alive() and _builder_client):
        print("[Builder Bot] Discord client not initialized or thread not running. Cannot send command.")
        return False
    
    if not _builder_ready_event.is_set() or not _builder_client.is_ready():
        print("[Builder Bot] Client not ready. Send command failed. Please ensure initialization completed.")
        return False
    
    try:
        channel_id = int(channel_id_str)
    except ValueError:
        print(f"[Builder Bot] Invalid Channel ID: {channel_id_str}. Must be an integer.")
        return False

    future = asyncio.run_coroutine_threadsafe(
        _send_message_async_for_builder(channel_id, message_content), 
        _builder_loop
    )
    try:
        result = future.result(timeout=15) 
        return result
    except asyncio.TimeoutError:
        print("[Builder Bot] Sending command message timed out waiting for async result.")
        return False
    except Exception as e:
        print(f"[Builder Bot] Exception waiting for send result: {e}")
        return False

def shutdown_builder_discord_sender():
    global _builder_client, _builder_loop, _builder_thread, _builder_ready_event
    
    if _builder_loop and _builder_client and not _builder_client.is_closed():
        print("[Builder Bot] Initiating shutdown of Discord client...")
        # Closing the client should eventually stop client.start() in _builder_login_and_run_minimal
        asyncio.run_coroutine_threadsafe(_builder_client.close(), _builder_loop)
        # Wait for the on_ready event to clear or a timeout, indicating logout might have processed
        # This is a bit indirect; a dedicated logout_complete event would be better.
        _builder_ready_event.wait(timeout=7) # Wait for client.close() to take effect
        print("[Builder Bot] Client close requested.")
    
    if _builder_loop and _builder_loop.is_running():
        _builder_loop.call_soon_threadsafe(_builder_loop.stop)
        print("[Builder Bot] Event loop stop requested.")
    
    if _builder_thread and _builder_thread.is_alive():
        print("[Builder Bot] Waiting for client thread to terminate...")
        _builder_thread.join(timeout=7) # Give thread time to exit after loop stop
        if _builder_thread.is_alive():
            print("[Builder Bot] Client thread did not terminate gracefully.")
        else:
            print("[Builder Bot] Client thread terminated.")
    
    _builder_client = None
    _builder_loop = None
    _builder_thread = None
    _builder_ready_event.clear()
    print("[Builder Bot] Builder Discord sender shutdown process complete.")