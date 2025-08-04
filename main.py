#!/usr/bin/env python3
"""
Debug version of main.py to identify error location
"""

import sys
import traceback
import os

def debug_main():
    """Main entry point with detailed error tracking"""
    try:
        print("Starting HUD Notes debug mode...")
        
        print("1. Importing core.application...")
        from core.application import HUDNotesApp
        print("   ✓ Import successful")
        
        print("2. Creating HUDNotesApp instance...")
        app = HUDNotesApp()
        print("   ✓ App instance created")
        
        print("3. Checking setup completion...")
        if hasattr(app, 'setup_complete') and app.setup_complete:
            print("   ✓ Setup completed successfully")
            print("4. Starting app.run()...")
            app.run()
        else:
            print("   ✗ Setup was cancelled or failed")
            print("Setup cancelled. Exiting...")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Missing module or incorrect import path")
        print("\nFull traceback:")
        traceback.print_exc()
        
    except AttributeError as e:
        print(f"❌ Attribute Error: {e}")
        print("This usually means a method or property doesn't exist")
        print("\nFull traceback:")
        traceback.print_exc()
        
    except KeyError as e:
        print(f"❌ Key Error: {e}")
        print("This usually means a dictionary key doesn't exist")
        print("\nFull traceback:")
        traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
    
    finally:
        input("Press Enter to exit...")

if __name__ == "__main__":
    debug_main()