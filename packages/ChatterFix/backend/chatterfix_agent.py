"""
ChatterFix AI Agent (Command Router)

This module serves as the central AI-powered command router for the ChatterFix application.
It uses the LLMRouter to interpret natural language commands, map them to available
backend functions (tools), and execute them with the appropriate parameters.
"""

import os
import json
from dotenv import load_dotenv

# Import the new LLM Router
from lib.llm_router import LLMRouter

# Import backend modules that contain the tools
from . import work_orders, inventory, assets, users, erp_tools, predictive, database

# Load environment variables
load_dotenv()

class ChatterFixAgent:
    """
    The primary AI agent for ChatterFix, handling both tool execution and chat.
    It uses an LLMRouter to select the best model for the job.
    """
    def __init__(self, chat_history=None):
        """Initializes the agent, the LLM Router, and loads tools."""
        if chat_history is None:
            chat_history = []
        try:
            self.llm_router = LLMRouter()
            self.chat_history = chat_history # Store history for chat context
            self.available_tools = self._get_available_tools()
            print("✅ ChatterFixAgent initialized successfully.")
        except Exception as e:
            print(f"❌ Error initializing ChatterFixAgent: {e}")
            self.llm_router = None
            self.chat_history = []
            self.available_tools = {}

    def _get_available_tools(self):
        """Returns the dictionary mapping tool names to functions."""
        return {
            # Work Order Tools
            "create_work_order": work_orders.create_work_order,
            "get_work_order": work_orders.get_work_order,
            "update_work_order_status": work_orders.update_work_order_status,
            "assign_work_order": work_orders.assign_work_order,
            "get_all_work_orders": work_orders.get_all_work_orders,
            # Inventory & Part Tools
            "get_part_by_id": inventory.get_part_by_id,
            "adjust_stock": inventory.adjust_stock,
            "get_low_stock_parts": inventory.get_low_stock_parts,
            # Asset Tools
            "get_asset": assets.get_asset,
            "get_all_assets": assets.get_all_assets,
            # User Tools
            "get_user_by_username": users.get_user_by_username,
            "get_all_users": users.get_all_users,
            # ERP Tools
            "get_vendor_data": erp_tools.get_vendor_data,
            "generate_purchase_order": erp_tools.generate_purchase_order,
            # Predictive Maintenance Tools
            "get_maintenance_forecast": predictive.get_maintenance_forecast,
        }

    def _get_tools_prompt_string(self):
        """Generates a string describing the available tools for the model prompt."""
        prompt_lines = ["Here are the tools you can use. Respond with a JSON object containing the tool name and its parameters.", ""]
        for name, func in self.available_tools.items():
            # Get the first line of the docstring as a summary
            doc = func.__doc__.strip().split('\n')[0]
            prompt_lines.append(f'- `"{name}"`: {doc}')
        return "\n".join(prompt_lines)

    def send_chat_message(self, message: str, override_model: str = None):
        """
        Handles conversational chat, streaming the response.
        Maintains context by appending to the chat history.
        """
        if not self.llm_router:
            yield "Error: LLM Router is not initialized."
            return

        try:
            # Append user message to history
            self.chat_history.append({"role": "user", "content": message})
            
            # Create a prompt that includes the history
            # This is a simplified approach; more sophisticated context management might be needed
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history])

            # Use the router to get a chat response
            # The router will stream the response if the underlying model supports it
            # NOTE: The current LLMRouter doesn't stream. This is a placeholder for that feature.
            response_text = self.llm_router.invoke_model(
                prompt,
                task_type='simple_chat',
                override_model=override_model
            )
            self.chat_history.append({"role": "assistant", "content": response_text})
            yield from response_text.split() # Simulate streaming by word

        except Exception as e:
            print(f"❌ Error during chat: {e}")
            yield f"Sorry, I encountered an error: {e}"

        except Exception as e:
            print(f"❌ Error during chat: {e}")
            yield f"Sorry, I encountered an error: {e}"

    def get_completion(self, prompt: str, override_model: str = None) -> str:
        """
        Gets a single, non-streamed completion from the LLM.
        Used for synchronous tasks like the CLI.
        """
        if not self.llm_router:
            return "Error: LLM Router is not initialized."
        try:
            return self.llm_router.invoke_model(
                prompt,
                task_type='simple_chat',
                override_model=override_model
            )
        except Exception as e:
            print(f"❌ Error in get_completion: {e}")
            return f"Error getting completion: {e}"

    def run_tool_command(self, command: str, context: dict = None, invoked_by_user: str = "system", dry_run: bool = False, override_model: str = None) -> dict:
        """
        Routes a natural language command to the appropriate tool and executes it.
        """
        if not self.llm_router:
            return {"error": "LLM Router is not configured."}

        context_str = f"\nContext: {json.dumps(context)}" if context else ""
        tools_prompt = self._get_tools_prompt_string()

        prompt = f"""
        You are ChatterFix, an AI assistant that handles industrial maintenance and ERP operations.
        Your task is to translate a natural language command into a specific function call.
        Respond ONLY with a single, valid JSON object containing the 'tool_name' and 'parameters'.

        {tools_prompt}

        Command: "{command}"
        {context_str}
        """

        try:
            print(f"🧠 Sending command to LLM Router: {command}")
            # Use the router to select the best model for tool use, allowing for an override
            response_text = self.llm_router.invoke_model(
                prompt,
                task_type='tool_use',
                override_model=override_model
            )

            # Clean up the response to get a valid JSON string
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()

            print(f"🤖 LLM Response (cleaned): {cleaned_response}")

            # Parse the JSON response from the model
            action = json.loads(cleaned_response)
            tool_name = action.get("tool_name")
            parameters = action.get("parameters", {})

            # Inject the user context for audit logging
            parameters['invoked_by_user'] = invoked_by_user

            if tool_name in self.available_tools:
                if dry_run:
                    print(f"DRY RUN: Would execute tool: `{tool_name}` with params: {parameters}")
                    return {"success": True, "tool": tool_name, "parameters": parameters, "mode": "dry_run"}

                print(f"🛠️ Executing tool: `{tool_name}` with params: {parameters}")
                # Execute the corresponding function
                tool_function = self.available_tools[tool_name]
                result = tool_function(**parameters)

                # Special handling for work order creation to include the ID
                if tool_name == "create_work_order":
                    return {"success": True, "tool": tool_name, "result": result, "document_id": result}

                return {"success": True, "tool": tool_name, "result": result}
            else:
                print(f"❌ Tool not found: {tool_name}")
                return {"error": f"Tool '{tool_name}' not found."}

        except json.JSONDecodeError:
            error_msg = "Failed to decode the model's JSON response."
            print(f"❌ {error_msg}")
            print(f"   Response was: {cleaned_response}")
            return {"error": error_msg, "raw_response": cleaned_response}
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def process_input(self, user_input: str, invoked_by_user: str = "system"):
        """
        Determines if the user input is a command or a chat message and routes it.
        This is the primary entry point for user interaction from the UI.
        It returns a dictionary for commands or a generator for chat.
        """
        if not self.llm_router:
            return {"error": "LLM Router is not configured."}

        # A prompt to ask the model to classify the intent
        classification_prompt = f'''
        Analyze the following user input and determine if it is a command for a tool or a general chat message.
        A command involves actions like 'create work order', 'get asset', 'update status', 'check inventory', 'order parts', 'generate report', 'find user', 'show me assets'.
        A chat message is more conversational, like 'hello', 'how are you', 'what can you do?'.

        Respond with a single, valid JSON object with a key "intent" which must be either "command" or "chat".

        User Input: "{user_input}"
        '''

        try:
            # Use a fast model for classification
            response_text = self.llm_router.invoke_model(
                classification_prompt,
                task_type='classification',
                override_model='gemini-1.5-flash-latest' # Or another fast model
            )
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            classification = json.loads(cleaned_response)
            intent = classification.get("intent")

            if intent == "command":
                print(f"🤖 Intent classified as 'command'. Routing to tool executor.")
                return self.run_tool_command(user_input, invoked_by_user=invoked_by_user)
            else: # Default to chat if intent is 'chat' or anything else
                print(f"💬 Intent classified as 'chat' (or fallback). Routing to chat handler.")
                return self.send_chat_message(user_input)

        except Exception as e:
            # If classification fails for any reason, it's safer to treat it as a chat message.
            print(f"❌ Error during intent classification: {e}. Defaulting to chat.")
            return self.send_chat_message(user_input)

# --- Testing ---

def test_agent(dry_run: bool = True):
    """
    Runs a sample test of the agent's command processing.
    """
    print("\n" + "="*50)
    print("          🧪 Running ChatterFix Agent Test 🧪")
    if dry_run:
        print("          (Dry Run Mode - No tools will be executed)")
    print("="*50 + "\n")

    agent = ChatterFixAgent()
    if not agent.llm_router:
        print("Agent initialization failed. Aborting test.")
        return

    # Define a mock user for testing
    test_user = "test_runner@chatterfix.com"

    # Test Case 1: Create a Work Order
    command1 = "The main conveyor belt is torn. We need to replace it. Priority is high."
    print(f"--- Test Case 1: Create Work Order ---")
    result1 = agent.run_tool_command(command1, dry_run=dry_run, invoked_by_user=test_user)
    print(f"▶️ Result: {result1}\n")

    # Test Case 2: Check Inventory (using a different model via override)
    command2 = "How many 5/8 inch bearings do we have in stock? Part number BR-54321."
    print(f"--- Test Case 2: Check Inventory (with override) ---")
    # This part of the test won't work until the agent method supports overrides
    result2 = agent.run_tool_command(command2, dry_run=dry_run, invoked_by_user=test_user, override_model='gpt-4o')
    # For now, we call it normally
    # result2 = agent.run_tool_command(command2, dry_run=dry_run, invoked_by_user=test_user)
    print(f"▶️ Result: {result2}\n")

    # Test Case 3: Order parts using ERP tool (complex reasoning)
    command3 = "We're critically low on bearings, please generate a PO for 100 units from Global Bearings Inc."
    print(f"--- Test Case 3: Generate Purchase Order (Complex Reasoning) ---")
    result3 = agent.run_tool_command(command3, dry_run=dry_run, invoked_by_user=test_user, override_model='claude-3-opus-20240229')
    print(f"▶️ Result: {result3}\n")
