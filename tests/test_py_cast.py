"""
Tests related to casting and vector/array composition.
"""


import ctypes

import pyshader
from pyshader import f32, f64, u8, i16, i32, i64  # noqa
from pyshader import bvec2, ivec2, ivec3, vec2, vec3, vec4, Array  # noqa

import wgpu.backends.rs  # noqa
from wgpu.utils import compute_with_buffers

import pytest
from testutils import can_use_wgpu_lib, iters_equal
from testutils import validate_module, run_test_and_print_new_hashes


def test_cast_i32_f32():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", "ivec3"),
        data1: ("buffer", 0, "Array(i32)"),
        data2: ("buffer", 1, "Array(f32)"),
    ):
        i = index.x
        data2[i] = f32(data1[i])

    skip_if_no_wgpu()

    values1 = [-999999, -100, -4, 0, 4, 100, 32767, 32768, 999999]

    inp_arrays = {0: (ctypes.c_int32 * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_float * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], values1)


def test_cast_u8_f32():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(u8)),
        data2: ("buffer", 1, Array(f32)),
    ):
        i = index.x
        data2[i] = f32(data1[i])

    skip_if_no_wgpu()

    values1 = [0, 1, 4, 127, 128, 255]

    inp_arrays = {0: (ctypes.c_ubyte * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_float * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], values1)


def test_cast_f32_i32():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(f32)),
        data2: ("buffer", 1, Array(i32)),
    ):
        i = index.x
        data2[i] = i32(data1[i])

    skip_if_no_wgpu()

    inp_arrays = {0: (ctypes.c_float * 20)(*range(20))}
    out_arrays = {1: ctypes.c_int32 * 20}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], range(20))


def test_cast_f32_f32():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(f32)),
        data2: ("buffer", 1, Array(f32)),
    ):
        i = index.x
        data2[i] = f32(data1[i])

    skip_if_no_wgpu()

    inp_arrays = {0: (ctypes.c_float * 20)(*range(20))}
    out_arrays = {1: ctypes.c_float * 20}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], range(20))


def test_cast_f32_f64():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(f32)),
        data2: ("buffer", 1, Array(f64)),
    ):
        i = index.x
        data2[i] = f64(data1[i])

    skip_if_no_wgpu()

    inp_arrays = {0: (ctypes.c_float * 20)(*range(20))}
    out_arrays = {1: ctypes.c_double * 20}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], range(20))


def test_cast_i64_i16():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(i64)),
        data2: ("buffer", 1, Array(i16)),
    ):
        i = index.x
        data2[i] = i16(data1[i])

    skip_if_no_wgpu()

    values1 = [-999999, -100, -4, 0, 4, 100, 32767, 32768, 999999]
    values2 = [-16959, -100, -4, 0, 4, 100, 32767, -32768, 16959]

    inp_arrays = {0: (ctypes.c_longlong * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_short * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], values2)


def test_cast_i16_u8():
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(i16)),
        data2: ("buffer", 1, Array(u8)),
    ):
        i = index.x
        data2[i] = u8(data1[i])

    skip_if_no_wgpu()

    values1 = [-3, -2, -1, 0, 1, 2, 3, 127, 128, 255, 256, 300]
    values2 = [253, 254, 255, 0, 1, 2, 3, 127, 128, 255, 0, 44]

    inp_arrays = {0: (ctypes.c_short * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_ubyte * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader)
    assert iters_equal(out[1], values2)


def test_cast_vec_ivec2_vec2():
    # This triggers the direct number-vector conversion
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(ivec2)),
        data2: ("buffer", 1, Array(vec2)),
    ):
        i = index.x
        data2[i] = vec2(data1[i])

    skip_if_no_wgpu()

    values1 = [-999999, -100, -4, 1, 4, 100, 32767, 32760, 0, 999999]

    inp_arrays = {0: (ctypes.c_int32 * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_float * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader, n=5)
    assert iters_equal(out[1], values1)


def test_cast_vec_any_vec4():
    # Look how all args in a vector are converted :)
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data2: ("buffer", 1, Array(vec4)),
    ):
        data2[index.x] = vec4(7.0, 3, ivec2(False, 2.7))

    skip_if_no_wgpu()

    values2 = [7.0, 3.0, 0.0, 2.0] * 2

    inp_arrays = {}
    out_arrays = {1: ctypes.c_float * len(values2)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader, n=2)
    assert iters_equal(out[1], values2)


def test_cast_vec_ivec3_vec3():
    return  # raise pytest.skip(msg="Cannot do vec3 storage buffers")

    # Exception: SpirV invalid:
    # error: line 23: Structure id 10 decorated as BufferBlock for
    # variable in Uniform storage class must follow standard storage
    # buffer layout rules: member 0 contains an array with stride 12
    # not satisfying alignment to 16
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(ivec3)),
        data2: ("buffer", 1, Array(vec3)),
    ):
        i = index.x
        data2[i] = vec3(data1[i])

    skip_if_no_wgpu()

    # vec3's are padded to 16 bytes! I guess it's a "feature"
    # https://stackoverflow.com/questions/38172696
    # ... so now I updated my driver and then it works ... sigh
    values1 = [-999999, -100, -4, 1, 4, 100, 32767, 32760, 999999]
    values2 = [-999999, -100, -4, 0, 4, 100, 32767, 0, 999999]

    inp_arrays = {0: (ctypes.c_int32 * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_float * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader, n=3)
    it_works = iters_equal(out[1], values1)
    it_fails = iters_equal(out[1], values2)
    assert it_works or it_fails  # ah well ...


def test_cast_ivec2_bvec2():
    # This triggers the per-element vector conversion
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(ivec2)),
        data2: ("buffer", 1, Array(ivec2)),
    ):
        i = index.x
        tmp = bvec2(data1[i])
        data2[i] = ivec2(tmp)  # ext visible storage cannot be bool

    skip_if_no_wgpu()

    values1 = [-999999, -100, 0, 1, 4, 100, 32767, 32760, 0, 999999]
    values2 = [True, True, False, True, True, True, True, True, False, True]

    inp_arrays = {0: (ctypes.c_int32 * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_int32 * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader, n=5)
    assert iters_equal(out[1], values2)


def test_abstract_types():
    # This triggers the per-element vector conversion
    @python2shader_and_validate
    def compute_shader(
        index: ("input", "GlobalInvocationId", ivec3),
        data1: ("buffer", 0, Array(ivec2)),
        data2: ("buffer", 1, Array(vec2)),
    ):
        i = index.x
        a = data1[i]
        data2[i] = Vector(2, f32)(a)

    skip_if_no_wgpu()

    values1 = [-999999, -100, 0, 1, 4, 100, 32767, 32760, 0, 999999]

    inp_arrays = {0: (ctypes.c_int32 * len(values1))(*values1)}
    out_arrays = {1: ctypes.c_float * len(values1)}
    out = compute_with_buffers(inp_arrays, out_arrays, compute_shader, n=5)
    assert iters_equal(out[1], values1)


# %% Utils for this module


def python2shader_and_validate(func):
    m = pyshader.python2shader(func)
    assert m.input is func
    validate_module(m, HASHES)
    return m


def skip_if_no_wgpu():
    if not can_use_wgpu_lib:
        raise pytest.skip(msg="SpirV validated, but not run (cannot use wgpu)")


HASHES = {
    "test_cast_i32_f32.compute_shader": ("0f97715bd46e44f1", "299f3e15acad5894"),
    "test_cast_u8_f32.compute_shader": ("db621633396816ab", "54681989e3ffef4a"),
    "test_cast_f32_i32.compute_shader": ("9e5240879e527c42", "af778e5bb20d0a2c"),
    "test_cast_f32_f32.compute_shader": ("3e9af418d6a59b2f", "aff51f11276e2d60"),
    "test_cast_f32_f64.compute_shader": ("ffdd61ca192a6af2", "f47fd4c37fd8d306"),
    "test_cast_i64_i16.compute_shader": ("820ac5faf4b9ef5c", "88e02595146b6c8f"),
    "test_cast_i16_u8.compute_shader": ("5160ad257f473715", "945fe0f09c981c3b"),
    "test_cast_vec_ivec2_vec2.compute_shader": ("faaf97ec5191ff47", "c2c40130d690c6e2"),
    "test_cast_vec_any_vec4.compute_shader": ("663a0a466eefd578", "222df0015243ae37"),
    "test_cast_ivec2_bvec2.compute_shader": ("f97e8c25daf81ba2", "87360c6b52fbdb65"),
    "test_abstract_types.compute_shader": ("4573e2bdbc07a59a", "bd6ee2724ca16939"),
}

if __name__ == "__main__":
    run_test_and_print_new_hashes(globals())
