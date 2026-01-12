"""
Simple demonstration of the faker integration logic.
This file can be run standalone to verify the logic works correctly.
"""

class MockSettings:
    """Mock Django settings for testing."""
    DEBUG = True

class FakerMock:
    """Mock Faker class for testing."""
    def company(self):
        return "Acme Corporation"
    
    def catch_phrase(self):
        return "Innovative solutions for modern problems"
    
    def url(self):
        return "https://example.com"

def get_faker_demo(debug=True):
    """Demo version of get_faker."""
    if not debug:
        return None
    try:
        return FakerMock()
    except:
        return None

def get_fake_client_data_demo(debug=True):
    """Demo version of get_fake_client_data."""
    fake = get_faker_demo(debug)
    if not fake:
        return {}
    
    return {
        'name': fake.company(),
        'description': fake.catch_phrase(),
        'url': fake.url(),
    }

class FakeDataMixinDemo:
    """Demo version of FakeDataMixin."""
    fake_data_function = 'get_fake_client_data'
    DEBUG = True
    
    def get_initial_parent(self):
        """Simulate parent class get_initial."""
        return {}
    
    def get_initial(self):
        """Get initial form data, with fake data added if in DEBUG mode."""
        initial = self.get_initial_parent()
        
        # Only add fake data if in DEBUG mode and function is specified
        if self.DEBUG and self.fake_data_function:
            try:
                # Get fake data
                fake_data = get_fake_client_data_demo(self.DEBUG)
                
                # Only add fake values for fields that aren't already set
                for key, value in fake_data.items():
                    if key not in initial or initial[key] is None:
                        initial[key] = value
            except:
                pass
        
        return initial

def test_debug_mode_enabled():
    """Test that fake data is added when DEBUG=True."""
    print("Test 1: DEBUG=True")
    mixin = FakeDataMixinDemo()
    mixin.DEBUG = True
    initial = mixin.get_initial()
    print(f"  Initial data: {initial}")
    assert 'name' in initial
    assert 'description' in initial
    assert 'url' in initial
    assert initial['name'] == 'Acme Corporation'
    print("  ✓ PASS: Fake data added when DEBUG=True\n")

def test_debug_mode_disabled():
    """Test that fake data is NOT added when DEBUG=False."""
    print("Test 2: DEBUG=False")
    mixin = FakeDataMixinDemo()
    mixin.DEBUG = False
    initial = mixin.get_initial()
    print(f"  Initial data: {initial}")
    assert initial == {}
    print("  ✓ PASS: No fake data when DEBUG=False\n")

def test_preserves_existing_values():
    """Test that existing initial values are preserved."""
    print("Test 3: Preserves existing values")
    
    class MixinWithExisting(FakeDataMixinDemo):
        def get_initial_parent(self):
            return {'name': 'Existing Name'}
    
    mixin = MixinWithExisting()
    mixin.DEBUG = True
    initial = mixin.get_initial()
    print(f"  Initial data: {initial}")
    assert initial['name'] == 'Existing Name', "Should preserve existing name"
    assert 'description' in initial, "Should add fake description"
    assert 'url' in initial, "Should add fake url"
    print("  ✓ PASS: Existing values preserved, other fields filled\n")

if __name__ == '__main__':
    print("=" * 60)
    print("Faker Integration Logic Verification")
    print("=" * 60)
    print()
    
    try:
        test_debug_mode_enabled()
        test_debug_mode_disabled()
        test_preserves_existing_values()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Fake data is only added when DEBUG=True")
        print("- Existing initial values are never overwritten")
        print("- The mixin works as expected")
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        exit(1)
