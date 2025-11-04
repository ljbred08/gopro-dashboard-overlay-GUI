import FreeSimpleGUI as sg
class CollapsibleSection:
    def __init__(self, layout, title, key, text_color='white', default_state=False):
        """
        Creates a collapsible section for PySimpleGUI windows
        
        Args:
            layout: The layout to be contained in the collapsible section
            title: Title text shown in the header
            key: Unique key for this section
            text_color: Color for the header text and symbol
            default_state: True for initially expanded, False for initially collapsed
        """
        self.SYMBOL_UP = '▸'
        self.SYMBOL_DOWN = '▾'
        self.key = key
        self.title = title
        self.layout = layout
        self.text_color = text_color
        self.default_state = default_state
        
    def _collapse(self, layout):
        """Creates a pinned column that can be made visible/invisible"""
        col = sg.pin(sg.Column(layout, key=f'{self.key}-CONTENT-', visible=self.default_state))
        return col
        
    def get_layout(self):
        """Returns the complete layout for the collapsible section"""
        return [
            [
                sg.T(self.SYMBOL_DOWN if self.default_state else self.SYMBOL_UP, 
                     enable_events=True, k=f'{self.key}-SYMBOL-', 
                     text_color=self.text_color),
                sg.T(self.title, enable_events=True, 
                     text_color=self.text_color, k=f'{self.key}-TITLE-')
            ],
            [self._collapse(self.layout)]
        ]

def handle_section_events(window, event, section):
    """Handles events for a collapsible section"""
    if event.startswith(f'{section.key}-SYMBOL-') or event.startswith(f'{section.key}-TITLE-'):
        is_open = window[f'{section.key}-SYMBOL-'].get() == section.SYMBOL_DOWN
        window[f'{section.key}-SYMBOL-'].update(
            section.SYMBOL_UP if is_open else section.SYMBOL_DOWN)
        window[f'{section.key}-CONTENT-'].update(visible=not is_open)
        return True
    return False

def handle_sections_events(window, event, sections):
    for section in sections:
        if handle_section_events(window, event, section):
            break