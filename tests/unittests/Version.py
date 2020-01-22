import pkg_resources


from storyscript.Version import get_version


def test_version_failure(patch):
    patch.object(
        pkg_resources,
        "get_distribution",
        side_effect=pkg_resources.DistributionNotFound,
    )
    version = get_version()
    pkg_resources.get_distribution.assert_called_with("storyscript")
    assert version == "0.0.0"
