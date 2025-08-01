import numpy as np
import numpy.testing as npt
from DriftAnalysisFramework.Interpolation import closest_values_slow, closest_values


# Assuming the definitions of closest_values and closest_values_optimized are available here
def test_closest_values():
    # Generate a sorted haystack array and some needle values
    haystack_array = np.geomspace(0.1, np.pi / 2, num=64)
    needle_values = np.random.rand(10) * np.pi / 2

    print(haystack_array, needle_values)


    # Run both functions
    l_closest_values_orig, h_closest_values_orig, l_closest_indices_orig, h_closest_indices_orig = closest_values_slow(needle_values, haystack_array)
    l_closest_values_opt, h_closest_values_opt, l_closest_indices_opt, h_closest_indices_opt = closest_values(needle_values, haystack_array)

    # Assert that the arrays returned by both functions are the same
    npt.assert_array_equal(l_closest_values_orig, l_closest_values_opt, err_msg="Lower closest values do not match")
    npt.assert_array_equal(h_closest_values_orig, h_closest_values_opt, err_msg="Higher closest values do not match")
    npt.assert_array_equal(l_closest_indices_orig, l_closest_indices_opt, err_msg="Lower closest indices do not match")
    npt.assert_array_equal(h_closest_indices_orig, h_closest_indices_opt, err_msg="Higher closest indices do not match")

    print("All tests passed successfully!")


# Run the test
test_closest_values()
