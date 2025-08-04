#!/usr/bin/env python3
import random
import sys

def roll_dice(dice_type, count=1):
    """Roll dice of specified type and count"""
    if dice_type <= 0:
        raise ValueError("Dice type must be positive")
    
    results = [random.randint(1, dice_type) for _ in range(count)]
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python dice_roller.py d<sides> [count]")
        print("Examples: python dice_roller.py d6")
        print("          python dice_roller.py d20 3")
        return
    
    dice_input = sys.argv[1].lower()
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if not dice_input.startswith('d'):
        print("Error: Dice type must start with 'd' (e.g., d6, d20)")
        return
    
    try:
        sides = int(dice_input[1:])
        results = roll_dice(sides, count)
        
        if count == 1:
            print(f"Rolling 1d{sides}: {results[0]}")
        else:
            total = sum(results)
            print(f"Rolling {count}d{sides}: {results} (total: {total})")
            
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()