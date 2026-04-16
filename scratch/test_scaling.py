import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

try:
    print("Testing Settings import...")
    from app.core.config import settings
    print(f"API_KEYS type: {type(settings.API_KEYS)}")
    print(f"API_KEYS value: {settings.API_KEYS}")
    
    print("\nTesting AI Services import...")
    from app.services.ai.model_ai import AtsResumeOptimizer
    from app.services.ai.ats_scoring import ATSScorerLLM
    
    print("\nTesting ATSScorerLLM initialization...")
    scorer = ATSScorerLLM()
    print(f"Scorer API Key selected: {scorer.api_key[:10]}...")
    
    print("\nTesting AtsResumeOptimizer initialization...")
    optimizer = AtsResumeOptimizer(resume="Test resume")
    print(f"Optimizer API Key selected: {optimizer.api_key[:10]}...")
    
    print("\nSUCCESS: All core components initialized correctly.")
except Exception as e:
    print(f"\nFAILURE: {e}")
    import traceback
    traceback.print_exc()
