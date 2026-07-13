"""
Quick integration test: create engine, populate, run 20 ticks, print stats.
"""
from engine import Engine

def main():
    eng = Engine(size=30)
    eng.populate(plants=40, herbivores=15, carnivores=3)

    print(f"Tick 0: {eng.stats}")
    for i in range(20):
        stats = eng.tick()
        print(f"Tick {stats['tick']:>3}: P={stats['plants']:>4} H={stats['herbivores']:>3} C={stats['carnivores']:>3}")

    print("\nDone. Engine ticking cleanly.")

if __name__ == "__main__":
    main()
