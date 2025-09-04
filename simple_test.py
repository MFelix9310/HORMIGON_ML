#!/usr/bin/env python3
"""
Test simple sin caracteres unicode para verificar que todo funciona
"""

def test_model():
    """Test basico del modelo"""
    print("=== TESTING MODEL ===")
    try:
        from model_handler_fixed import ConcreteModelHandler
        handler = ConcreteModelHandler()
        
        if handler.is_loaded:
            print("OK - Model loaded successfully")
            
            # Test prediction
            test_data = {
                'Cemento_kg_m3': 200,
                'Escoria_Alto_Horno_kg_m3': 200,
                'Ceniza_Volante_kg_m3': 100,
                'Agua_kg_m3': 130,
                'Superplastificante_kg_m3': 25,
                'Agregado_Grueso_kg_m3': 1000,
                'Agregado_Fino_kg_m3': 700,
                'Edad_dias': 28
            }
            
            result = handler.predict_strength(test_data)
            resistance = result['resistencia_predicha_kg_cm2']
            print(f"OK - Prediction: {resistance:.2f} kg/cm2")
            print(f"OK - Classification: {result['clasificacion_nec']}")
            return True
        else:
            print("ERROR - Model not loaded")
            return False
            
    except Exception as e:
        print(f"ERROR - {e}")
        return False

def test_gui_components():
    """Test basico de componentes GUI"""
    print("\n=== TESTING GUI COMPONENTS ===")
    try:
        from ui_components import SliderSpinBoxWidget, CircularGauge
        from PyQt6.QtWidgets import QApplication
        
        # Create application if needed
        if not QApplication.instance():
            app = QApplication([])
        
        # Test slider component
        slider = SliderSpinBoxWidget("Test", 0, 100, 50)
        slider.set_value(75)
        value = slider.get_value()
        
        if abs(value - 75) < 0.1:
            print("OK - SliderSpinBoxWidget works")
        else:
            print("ERROR - SliderSpinBoxWidget failed")
            return False
        
        # Test gauge
        gauge = CircularGauge(0, 600, 400, "Test")
        print("OK - CircularGauge created")
        
        return True
        
    except Exception as e:
        print(f"ERROR - {e}")
        return False

def test_main_app():
    """Test aplicacion principal"""
    print("\n=== TESTING MAIN APPLICATION ===")
    try:
        from predictor_gui import ConcreteStrengthPredictor
        from PyQt6.QtWidgets import QApplication
        
        if not QApplication.instance():
            app = QApplication([])
        
        window = ConcreteStrengthPredictor()
        
        if window.model_handler.is_loaded:
            print("OK - Main application created")
            print("OK - Model loaded in GUI")
            
            # Test preset loading
            window._load_preset("C20 - Uso General")
            print("OK - Preset loading works")
            
            return True
        else:
            print("ERROR - Model not loaded in GUI")
            return False
            
    except Exception as e:
        print(f"ERROR - {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("STARTING COMPREHENSIVE TESTS")
    print("=" * 50)
    
    tests = [
        ("Model Loading", test_model),
        ("GUI Components", test_gui_components), 
        ("Main Application", test_main_app)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"CRITICAL ERROR in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    all_passed = True
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name:<20}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("SUCCESS - ALL TESTS PASSED")
        print("Application is ready to use: python main.py")
    else:
        print("FAILURE - Some tests failed")