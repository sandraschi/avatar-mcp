try:
    import avatarmcp
    print("✅ Import OK")
    print(f"✅ Module location: {avatarmcp.__file__}")
    
    try:
        import avatarmcp.server
        print("✅ avatarmcp.server import: OK")
    except ImportError as e:
        print(f"❌ avatarmcp.server import failed: {e}")
    
    try:
        from avatarmcp.core.mcp_server import MCPServer
        print("✅ MCPServer import: OK")
    except ImportError as e:
        print(f"❌ MCPServer import failed: {e}")
        
    try:
        from avatarmcp.__main__ import main
        print("✅ main function import: OK")
    except ImportError as e:
        print(f"❌ main function import failed: {e}")
        
except ImportError as e:
    print(f"❌ avatarmcp import failed: {e}")
