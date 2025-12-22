
import sys
from config.container import container

def test_db():
    print("Testing DB Connection...")
    try:
        # Test get_lead
        phone = "+34625852546" 
        lead = container.db.get_lead(phone)
        print(f"Lead found: {lead is not None}")
        
        # Test save_lead (dummy update)
        if lead:
            print("Attempting to save lead (no change)...")
            container.db.save_lead(lead)
            print("Save lead successful.")
        else:
            print("Lead not found, skipping save test.")
            
    except Exception as e:
        print(f"DB Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_db()
