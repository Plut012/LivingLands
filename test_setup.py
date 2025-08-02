#!/usr/bin/env python3
"""
Test script to verify the development setup works
"""

import sys
import os
from pathlib import Path

def test_backend_imports():
    """Test that all backend modules can be imported"""
    print("🧪 Testing backend imports...")
    
    # Add backend to path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    try:
        import models
        print("  ✅ models.py")
        
        import dice
        print("  ✅ dice.py")
        
        import actions
        print("  ✅ actions.py")
        
        import world
        print("  ✅ world.py")
        
        import database
        print("  ✅ database.py")
        
        import llm_client
        print("  ✅ llm_client.py")
        
        print("✅ All backend modules import successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_game_logic():
    """Test basic game logic"""
    print("\n🎲 Testing game logic...")
    
    try:
        from models import create_knight, VirtueType
        from dice import roll_d6, make_save
        
        # Test character creation
        knight = create_knight("Test Knight", 12, 10, 8, 6)
        print(f"  ✅ Created knight: {knight.name}")
        
        # Test dice rolling
        roll = roll_d6()
        print(f"  ✅ Dice roll: {roll}")
        
        # Test save
        success, value = make_save(knight.virtues[VirtueType.VIGOUR])
        print(f"  ✅ Save roll: {success} ({value})")
        
        print("✅ Game logic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Game logic error: {e}")
        return False

def test_frontend_files():
    """Test that frontend files exist"""
    print("\n🌐 Testing frontend files...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    required_files = [
        "index.html",
        "game.js", 
        "styles.css",
        "terminal.js"
    ]
    
    all_exist = True
    for file in required_files:
        if (frontend_dir / file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    if all_exist:
        print("✅ All frontend files found")
    else:
        print("❌ Some frontend files missing")
    
    return all_exist

def main():
    print("🏰 Mythic Bastionlands Setup Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if test_backend_imports():
        tests_passed += 1
    
    if test_game_logic():
        tests_passed += 1
        
    if test_frontend_files():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 Setup looks good! Ready to start development.")
        print("\nNext steps:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Run: ollama serve")
        print("3. Run: ollama pull llama3.2")
        print("4. Run: python start_dev.py")
    else:
        print("⚠️  Some issues found. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)