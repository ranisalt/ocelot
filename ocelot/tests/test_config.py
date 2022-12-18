import io

from ..config import load_config


def test_load_config():
    fp = io.StringIO(
        """
        [worlds.default]
        id = 0
        name = "Antica"
        pvp-type = "pvp"
        address-protected = "prod-cf-eu.tibia.com"
        port-protected = 7171
        address-unprotected = "prod-lb-eu.tibia.com"
        port-unprotected = 7171
        map = { type = "otbm", file = "data/world/map.otbm" }
        """
    )

    config = load_config(fp)
    world = config.worlds["default"]
    assert world.id == 0
    assert world.name == "Antica"
    assert world.pvp == "pvp"
    assert world.address_protected == "prod-cf-eu.tibia.com"
    assert world.port_protected == 7171
    assert world.address_unprotected == "prod-lb-eu.tibia.com"
    assert world.port_unprotected == 7171


def test_load_config_pvp_types():
    base = """
        [worlds.default]
        id = 0
        name = "Antica"
        address-protected = "prod-cf-na.tibia.com"
        port-protected = 7171
        address-unprotected = "prod-lb-na.tibia.com"
        port-unprotected = 7171
        map = { type = "otbm", file = "data/world/map.otbm" }
        """

    fp = io.StringIO(
        f"""
        {base}
        pvp-type = "no-pvp"
        """
    )

    config = load_config(fp)
    world = config.worlds["default"]
    assert world.pvp == "no-pvp"

    fp = io.StringIO(
        f"""
        {base}
        pvp-type = "pvp-enforced"
        """
    )

    config = load_config(fp)
    world = config.worlds["default"]
    assert world.pvp == "pvp-enforced"
