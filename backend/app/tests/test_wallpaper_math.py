from app.engines.wallpaper_math import order_rolls, roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_order_rolls_rounds_up():
    # 11 卷基础量：10% 备损 -> 12.1 -> 13 卷；0% -> 11 卷
    assert order_rolls(11, 10) == 13
    assert order_rolls(11, 0) == 11
    # 整除时取整误差不被误升卷：10 * 1.1 = 11
    assert order_rolls(10, 10) == 11


def test_validate_waste_pct_bounds():
    from app.engines.wallpaper_math import validate_waste_pct

    assert validate_waste_pct(0) == 0.0
    assert validate_waste_pct(100) == 100.0
    for bad in (-1, -0.1, 100.1):
        try:
            validate_waste_pct(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{bad} should be rejected")
