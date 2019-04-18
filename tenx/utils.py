def tenxlibrary_naming_scheme(library):
    library.name = "_".join(
        ["SCRNA10X", library.chips.lab_name, str(library.chips.pk).zfill(4), str(library.chip_well).zfill(4)]
    )
    library.save()

def tenxpool_naming_scheme(pool):
    pool.pool_name = "".join(["TENXPOOL", str(pool.id).zfill(4)])
    pool.save()