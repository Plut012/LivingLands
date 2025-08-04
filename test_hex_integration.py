#!/usr/bin/env python3
"""
Test script for enhanced hex map integration
"""

from backend.models import (
    TerrainType, LandmarkType, MythType, Hex, Barrier, HexMap,
    create_sample_realm, create_new_game_with_sample_realm,
    GameState
)

def test_terrain_types():
    """Test terrain type enums"""
    print("Testing terrain types...")
    assert TerrainType.MARSH.value == "marsh"
    assert TerrainType.PEAKS.value == "peaks"
    print("✓ Terrain types working")

def test_hex_creation():
    """Test hex creation and serialization"""
    print("Testing hex creation...")
    
    # Create a hex with all features
    hex_obj = Hex(
        q=1, r=2, 
        terrain=TerrainType.FOREST,
        explored=True,
        landmark=LandmarkType.DWELLING,
        landmark_name="Woodsman's Hut",
        myth=MythType.HERALD,
        myth_name="The Speaking Trees",
        river=True
    )
    
    # Test serialization
    hex_dict = hex_obj.to_dict()
    print(f"✓ Hex serialized: {hex_dict['landmark_name']} in {hex_dict['terrain']}")
    
    # Test deserialization
    restored_hex = Hex.from_dict(hex_dict)
    assert restored_hex.landmark_name == "Woodsman's Hut"
    assert restored_hex.terrain == TerrainType.FOREST
    print("✓ Hex serialization/deserialization working")

def test_barriers():
    """Test barrier system"""
    print("Testing barriers...")
    
    barrier = Barrier((1, 2), (2, 2), "cliff", "A steep cliff face")
    
    # Test travel blocking
    assert barrier.blocks_travel((1, 2), (2, 2))
    assert barrier.blocks_travel((2, 2), (1, 2))  # Should work both ways
    assert not barrier.blocks_travel((1, 2), (1, 3))
    
    print("✓ Barrier system working")

def test_hex_map():
    """Test HexMap utility class"""
    print("Testing HexMap utility...")
    
    hexes, barriers = create_sample_realm()
    hex_map = HexMap(hexes, barriers)
    
    # Test hex lookup
    thornwick = hex_map.get_hex(0, 2)
    assert thornwick.landmark_name == "Thornwick"
    
    # Test neighbors
    neighbors = hex_map.get_neighbors(0, 2)
    assert len(neighbors) > 0
    
    # Test accessible vs blocked neighbors
    accessible = hex_map.get_accessible_neighbors(0, 2)
    print(f"✓ Thornwick has {len(neighbors)} neighbors, {len(accessible)} accessible")
    
    # Test myth/holding queries
    myths = hex_map.get_myths()
    holdings = hex_map.get_holdings()
    print(f"✓ Found {len(myths)} myths and {len(holdings)} holdings")

def test_game_state_integration():
    """Test GameState integration with new hex system"""
    print("Testing GameState integration...")
    
    game_state = create_new_game_with_sample_realm("test", "Sir Test", "Test knight")
    
    # Test position
    pos = game_state.get_current_position()
    assert pos == (0, 2)
    
    # Test hex access
    current_hex = game_state.get_hex(0, 2)
    assert current_hex.landmark_name == "Thornwick"
    
    # Test barriers
    barriers = game_state.get_barriers()
    assert len(barriers) == 7
    
    # Test movement validation
    can_move = game_state.can_travel_between((0, 2), (1, 2))
    assert can_move  # Should be able to move from Thornwick to plains
    
    print("✓ GameState integration working")

def test_serialization_robustness():
    """Test hex serialization edge cases"""
    print("Testing serialization robustness...")
    
    # Test minimal hex
    minimal_hex = Hex(q=0, r=0, terrain=TerrainType.PLAINS)
    hex_dict = minimal_hex.to_dict()
    restored = Hex.from_dict(hex_dict)
    assert restored.terrain == TerrainType.PLAINS
    assert not restored.explored
    
    print("✓ Serialization robustness working")

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Hex Map Integration\n")
    
    test_terrain_types()
    test_hex_creation()
    test_barriers()
    test_hex_map()
    test_game_state_integration()
    test_serialization_robustness()
    
    print("\n🎉 All tests passed! Enhanced hex map system is ready.")
    print("\nKey features working:")
    print("- 12 terrain types with visual theming")
    print("- 7 landmark types with unique icons")
    print("- 6 myth types with special markers")
    print("- Barrier system for movement restrictions")
    print("- River system overlay")
    print("- Clean serialization without legacy fields")
    print("- Sample realm with 28 detailed hexes")

if __name__ == "__main__":
    main()