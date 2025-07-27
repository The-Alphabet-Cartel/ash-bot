#!/usr/bin/env python3
"""
Session Token Diagnostic Script
Helps debug SESSION_TOKEN issues for Ash Bot API server
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load .env file if it exists"""
    env_file = Path('../.env')
    if env_file.exists():
        print(f"📁 Found .env file: {env_file.absolute()}")
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line.startswith('SESSION_TOKEN='):
                    token_value = line.split('=', 1)[1]
                    print(f"📋 Found SESSION_TOKEN on line {line_num}")
                    return token_value
        print("❌ No SESSION_TOKEN found in .env file")
    else:
        print("❌ No .env file found")
    return None

def test_session_token(token_value):
    """Test if a session token is valid for Fernet"""
    print(f"\n🔍 Testing SESSION_TOKEN...")
    print(f"📏 Length: {len(token_value)} characters")
    print(f"🔤 First 20 chars: {token_value[:20]}...")
    print(f"🔤 Last 10 chars: ...{token_value[-10:]}")
    
    try:
        from cryptography.fernet import Fernet
        print("✅ cryptography library available")
    except ImportError:
        print("❌ cryptography library not installed")
        print("💡 Install with: pip install cryptography")
        return False
    
    # Test as-is
    try:
        test_key = token_value.encode() if isinstance(token_value, str) else token_value
        fernet = Fernet(test_key)
        print("✅ SESSION_TOKEN is valid Fernet key!")
        
        # Test encryption/decryption
        test_message = b"test message"
        encrypted = fernet.encrypt(test_message)
        decrypted = fernet.decrypt(encrypted)
        if decrypted == test_message:
            print("✅ Encryption/decryption test passed")
            return True
        else:
            print("❌ Encryption/decryption test failed")
    except Exception as e:
        print(f"❌ Fernet validation failed: {e}")
    
    # Test if it's a base64 encoded 32-byte key
    try:
        import base64
        decoded = base64.urlsafe_b64decode(token_value.encode())
        print(f"📐 Decoded length: {len(decoded)} bytes (need 32)")
        if len(decoded) == 32:
            print("✅ Correct length after base64 decode")
            fernet = Fernet(token_value.encode())
            print("✅ Valid Fernet key after base64 check")
            return True
        else:
            print(f"❌ Wrong length: got {len(decoded)} bytes, need 32")
    except Exception as e:
        print(f"❌ Base64 decode failed: {e}")
    
    return False

def generate_new_token():
    """Generate a new valid session token"""
    try:
        from cryptography.fernet import Fernet
        new_token = Fernet.generate_key()
        print(f"\n🔑 Generated new SESSION_TOKEN:")
        print(f"SESSION_TOKEN={new_token.decode()}")
        print(f"\n📝 Add this to your .env file:")
        print(f"SESSION_TOKEN={new_token.decode()}")
        return new_token.decode()
    except Exception as e:
        print(f"❌ Failed to generate new token: {e}")
        return None

def main():
    print("🔐 Ash Bot Session Token Diagnostic")
    print("=" * 40)
    
    # Check environment variable
    env_token = os.getenv('SESSION_TOKEN')
    if env_token:
        print(f"🌍 Found SESSION_TOKEN in environment")
        if test_session_token(env_token):
            print("\n✅ Your SESSION_TOKEN is working correctly!")
            return
    else:
        print("❌ No SESSION_TOKEN in environment")
    
    # Check .env file
    file_token = load_env_file()
    if file_token:
        if test_session_token(file_token):
            print("\n✅ Your .env SESSION_TOKEN is valid!")
            print("💡 Make sure to restart your Docker containers to pick up the change")
            return
    
    # Neither worked, generate new one
    print("\n❌ No valid SESSION_TOKEN found")
    print("🔧 Generating a new one...")
    
    new_token = generate_new_token()
    if new_token:
        # Try to update .env file
        env_file = Path('.env')
        if env_file.exists():
            print(f"\n📝 Updating .env file...")
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Replace or add SESSION_TOKEN
            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith('SESSION_TOKEN='):
                    lines[i] = f"SESSION_TOKEN={new_token}\n"
                    found = True
                    break
            
            if not found:
                lines.append(f"SESSION_TOKEN={new_token}\n")
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print("✅ Updated .env file with new SESSION_TOKEN")
            print("🔄 Restart your bot to use the new token:")
            print("   docker-compose down && docker-compose up -d")
        else:
            print("📝 Create a .env file with this SESSION_TOKEN")

if __name__ == "__main__":
    main()