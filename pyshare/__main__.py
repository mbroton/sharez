from pyshare import main


try:
    raise SystemExit(main())
except KeyboardInterrupt:
    print("\rShutting down...")
