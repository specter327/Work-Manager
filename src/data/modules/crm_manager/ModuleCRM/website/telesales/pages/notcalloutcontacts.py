# Library import
from .webpageheader import WebPageHeader
from .contactslistsheader import ContactsList

# Classes definition
class NotCalloutContactsPage(ContactsList, WebPageHeader):
    def is_current_page(self, use_javascript: bool = True):
        if use_javascript:
            query_code = """function isCurrentPage(){
    // Search the frame document element
    let frameDocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (frameDocumentElement === null){
        return null;
    }

    // Verify the frame document URL
    if (!frameDocumentElement.src.includes("/apps/callout/names/home.html")){
        return false
    }

    // Verify the internal frame document content URL
    if (frameDocumentElement.contentDocument.URL.includes("/apps/callout/names/notcallout.html")){
        return true;
    } else {
        return false;
    }
}

// Use
return isCurrentPage();
"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError