# Library import
from __future__ import annotations

# Classes definition
class WebFolder:
    "This class provides a abstract representation of a web folder, which provides structure and organization to the resources"

    def __init__(self,
        name: str,
        website: website.WebSite, # pyright: ignore[reportUndefinedVariable]
        folder_parent: webfolder.WebFolder = None # type: ignore
    ):
        """Parameters example:
            name: search
            website: WebSite object instance
            folder_parent: WebFolder object instance (only if the actual WebFolder is contained on that WebFolder parent) | None
        """

        # Property definition
        self.name = name
        self.website = website
        self.folder_parent = folder_parent

        # Internal structures
        self.subfolders = {}
        self.pages = {}

    @property
    def path(self) -> str:
        if self.folder_parent:
            return f"{self.folder_parent.path}/{self.name}"
        else:
            return f"{self.name}"
    
    @property
    def base_url(self) -> str:
        return f"{self.website.base_url}{self.path}"
    
    # Public methods
    def register_folder(self, name: str, folder: webfolder.WebFolder) -> bool: # pyright: ignore[reportUndefinedVariable]
        "This function appends a new WebFolder object instance to the internal web folders"
        self.subfolders[name] = folder

        return True
    
    def register_page(self, name: str, page: webpage.WebPage) -> bool: # type: ignore
        "This function appends a new WebPage object instance to the internal web pages"
        self.pages[name] = page

        return True
    
    def get_folder(self, name: str) -> webfolder.WebFolder | None: # pyright: ignore[reportUndefinedVariable]
        "This function retrieves a specified WebFolder by its name"
        return self.subfolders.get(name)
    
    def get_page(self, name: str) -> webpage.WebPage | None: # pyright: ignore[reportUndefinedVariable]
        "This function retrieves a specified WebPage by its name"
        return self.pages.get(name)
    