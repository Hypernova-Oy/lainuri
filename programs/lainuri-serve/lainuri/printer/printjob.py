class PrintJob:
  def __init__(self, receipt_type: str, data: dict = {}):
    if receipt_type not in ('checkin', 'checkout', 'test'): raise ValueError(f"Unknown receipt_type '{receipt_type}'!")

    """
    data: used to populate placeholders in the Jinja2 template. Should contain atleast the following keys:
      header: str
      footer: str
      items: list
      user: dict
    """
    self.data = data
    """
    _css: Overload all other css definitions with this. Mostly useful for testing.
    """
    self.css = None #str
    """
    _page_increment: Granularity to look for the minimum height of the document to fit all the content. the bigger the faster, but more paper is wasted with trailing margin.
    """
    self._page_increment = 10
    """
    How many times we needed to iterate weasyprint's page rendering to find a reasonably close single page height
    """
    self._page_size_lookups = 0
    """
    Where is the receipt image saved
    """
    self._png_file_path = None #pathlib.Path
    """
    The actual HTML to print
    """
    self._printable_html = None #str
    self._receipt_template = None #str - contents of a jinja2 file
    self._run_time = None #int seconds with floating
    self._template_backend = None #str koha / lainuri
    self._template_file_path = None #Path
    self._type = receipt_type
