    ```
    single_cell_lims/
        account/
            stuff
        api/
            stuff
        core/
            templates/ 
            models.py 
            urls.py
            views.py
            other_stuff
        dlp/
            apps.py
            models.py
            urls.py
        tenx/
            apps.py
            models.py
            urls.py
        pbal/
            apps.py
            models.py
            urls.py
        sisyphus/
            stuff
        colossus/
            __init__.py
            urls.py
            settings.py
        db-schema/
            stuff
        scripts/
            stuff
        static/
            favicon.ico
            scripts.js
            style.css
            up-arrow.png
        taggit/
            stuff
        templates/
            stuff
        manage.py
        other_stuff
    ```

# Proposal: Restructure Colossus based on the above project layout.
Based on this [layout](http://www.revsys.com/blog/2014/nov/21/recommended-django-project-layout/).

`core/templates/`: Have one set of static html pages if possible, use Liquid template language to change which forms are passed into rendering, based on which forms are delivered by `core/views.py`.

`core/models.py`: Contains ChipRegion, SubLibraryInformation, MetadataField, ChipRegionMetadataField, Library\*, Sequencing\*, Lane ( which are all inherited by dlp, tenx, pbal). Also whatever helpers etc. that are already present.

`core/urls.py`: Contains paths to `sample_list`, `sample_detail`, `sample_create`, `sample_update`, and `sample_delete` views.

`core/views.py`: All other `urls.py` files in the project point to this file.


`dlp/models.py`, `tenx/models.py`, and `pbal/models.py`: Each contain some variation of ChipRegion, SubLibraryInformation, MetadataField, ChipRegionMetadataField, Library\*, Sequencing\*, and Lane. Each inherits from `core/models.py` using [super()](https://docs.python.org/2/library/functions.html#super).
