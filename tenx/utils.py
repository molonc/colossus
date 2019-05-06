def tenxlibrary_naming_scheme(library):
    return "_".join(
        ["SCRNA10X", library.chips.lab_name, "CHIP" + str(library.chips.pk).zfill(4), str(library.chip_well).zfill(4)]
    )


def tenxpool_naming_scheme(pool):
    return "".join(["TENXPOOL", str(pool.id).zfill(4)])
