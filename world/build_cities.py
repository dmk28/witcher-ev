"""
City Builder - Main Script
Choose which city or cities to build for the Witcher RPG

Usage:
    python world/build_cities.py vengerberg     # Build only Vengerberg
    python world/build_cities.py novigrad       # Build only Novigrad
    python world/build_cities.py both           # Build both cities
    python world/build_cities.py                # Interactive menu
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def show_menu():
    """Display city builder menu."""
    print()
    print("=" * 70)
    print("WITCHER RPG - CITY BUILDER")
    print("=" * 70)
    print()
    print("Available cities:")
    print()
    print("  1. Vengerberg (32x32 grid, 1,024 rooms)")
    print("     - Temple District, Royal Quarter, Market Ward")
    print("     - Craftsmen Quarter, River Ward")
    print("     - Northern Woods, Iron Mine, Pontar River")
    print()
    print("  2. Novigrad (40x40 grid, 1,600 rooms)")
    print("     - Temple District, Gildorf, The Bits")
    print("     - Harborside, Glory Lane, Putrid Grove")
    print("     - Color-coded districts, largest city")
    print("     - STAFF-LOCKED connection to Vengerberg")
    print()
    print("  3. Both cities (2,624 rooms total)")
    print("     - Build complete interconnected world")
    print()
    print("  4. Exit")
    print()
    print("=" * 70)
    print()


def build_vengerberg():
    """Build Vengerberg city."""
    print("\n" + "=" * 70)
    print("BUILDING VENGERBERG...")
    print("=" * 70 + "\n")

    # Import and run Vengerberg builder
    import world.vengerberg_builder as vb
    vb.main()


def build_novigrad():
    """Build Novigrad city."""
    print("\n" + "=" * 70)
    print("BUILDING NOVIGRAD...")
    print("=" * 70 + "\n")

    # Import and run Novigrad builder
    import world.novigrad_builder as nb
    nb.main()


def build_both():
    """Build both cities."""
    print("\n" + "=" * 70)
    print("BUILDING BOTH CITIES")
    print("=" * 70 + "\n")

    print("This will create 2,624 rooms total. This may take several minutes.")
    print()

    # Build Vengerberg first
    build_vengerberg()

    print()
    print("-" * 70)
    print()

    # Then build Novigrad
    build_novigrad()

    print()
    print("=" * 70)
    print("BOTH CITIES COMPLETE!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  Vengerberg: 1,024 rooms + ~4,000 exits")
    print("  Novigrad: 1,600 rooms + ~6,200 exits")
    print("  Total: 2,624 rooms interconnected")
    print()
    print("Cities are connected via staff-locked waystones.")
    print("Use 'activate waystone to <city>' with Builder permissions.")
    print()


def main():
    """Main function."""
    # Check for command-line argument
    if len(sys.argv) > 1:
        choice = sys.argv[1].lower()

        if choice in ['vengerberg', 'v', '1']:
            build_vengerberg()
        elif choice in ['novigrad', 'n', '2']:
            build_novigrad()
        elif choice in ['both', 'all', '3']:
            build_both()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Valid options: vengerberg, novigrad, both")
            sys.exit(1)

    else:
        # Interactive menu
        while True:
            show_menu()

            try:
                choice = input("Enter your choice (1-4): ").strip()

                if choice == '1':
                    build_vengerberg()
                    break
                elif choice == '2':
                    build_novigrad()
                    break
                elif choice == '3':
                    build_both()
                    break
                elif choice == '4':
                    print("\nExiting city builder.")
                    sys.exit(0)
                else:
                    print("\n|rInvalid choice. Please enter 1-4.|n")
                    input("Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\nExiting city builder.")
                sys.exit(0)


if __name__ == '__main__':
    main()
