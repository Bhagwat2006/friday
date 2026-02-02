import sys
import time
from core.voice import VoiceEngine
from core.brain import FridayBrain
from core.executor import Executor
from config import settings

def main():
    print(f"Initializing {settings.AI_NAME}...")
    
    # Initialize Core Modules
    voice = VoiceEngine()
    brain = FridayBrain()
    executor = Executor()
    
    voice.speak(f"{settings.AI_NAME} is online. Systems operational. Ready for instructions, {settings.USER_NAME}.")
    
    while True:
        try:
            # 1. Listen
            user_input = voice.listen()
            
            if not user_input:
                continue
                
            if "stop" in user_input or "exit" in user_input or "shutdown" in user_input:
                voice.speak(f"Shutting down. Goodbye, {settings.USER_NAME}.")
                break

            # 2. Think
            decision = brain.think(user_input)
            
            # 3. Act / Speak
            if decision.get("response"):
                voice.speak(decision["response"])
            
            if decision.get("type") == "action" and decision.get("code"):
                print(f"Executing: {decision['code']}")
                result = executor.execute(decision["code"])
                
                # Feedback loop: Provide execution result back to Brain context
                if result:
                    print(f"Result: {result}")
                    # We can add this to brain history for context in next turn
                    brain.history.append({"role": "system", "content": f"Execution Result: {result}"})
                    
                    # If it was an error, let the user know
                    if "Error" in result:
                        voice.speak(f"I encountered an error executing that task, Boss. {result}")

        except KeyboardInterrupt:
            print("\nForce shutdown.")
            break
        except Exception as e:
            print(f"Critical Error: {e}")
            voice.speak("I encountered a critical system error.")

if __name__ == "__main__":
    main()
