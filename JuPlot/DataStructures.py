from enum import Enum
from utils import inspect_dictionary_structure

class Backend(Enum):
    matplotlib = 1
    plotly = 2
    empty = 3

# Ver si se puede reducir en un init
class PlotType(Enum):
    # 2 vars
    scatter = 1 #marker and line
    heatmap = 4
    lmplot = 13
    # contour = 6
    # histogram2d = 10

    # 1 var
    box = 7
    violin = 8
    histogram = 9


    # Categoric
    bar = 2
    pie = 3
    
    # distplot pairplot

# THEME -> toda la informacion relevante a la personalizacion
class ThemeElement(Enum):
    figure = 1
    title = 2
    axes = 3
    legend = 4
    color_palette = 5
    font = 6

class Theme:

    @staticmethod
    def bases(element):
        if element == ThemeElement.color_palette:
            return dict(
                colors = (tuple, list)
            )
        
        elif element == ThemeElement.figure:
            return dict(
                figsize = (tuple, list), #(height, width)
                dpi = int,
                paper_color = (tuple, list),
                plot_background_color = (tuple, list)
            )
        
        elif element == ThemeElement.font:
            return dict(
                size = int,
                color = (tuple, list), 
                family = str,
                weight = str
            )
        
        elif element == ThemeElement.title:
            return dict(
                font = Theme.bases(ThemeElement.font),
                position = (tuple, list)
            )

        elif element == ThemeElement.axes:
            return dict(
                    font = Theme.bases(ThemeElement.font)
                )

        elif element == ThemeElement.legend:
            return dict(title = dict(
                        font = Theme.bases(ThemeElement.font)
                    ),
                    font = Theme.bases(ThemeElement.font) 
                )
        
        # Else

    def __init__(self, **kwargs):
        self.__elements = {key: None for key in ThemeElement}

        for key, dic in kwargs.items():
            try:
                element = ThemeElement[key]
            except:
                raise Exception(f"{key} not in theme elements")
            
            inspect_dictionary_structure(Theme.bases(element), dic, strict_structure= False)
            self.__elements[element] = dic
        

    def edit_property(self, element, key, value):
        possible_types = self.bases(element)[key]
        if isinstance(possible_types, dict):
            possible_types = (dict)
        assert isinstance(value, possible_types), f"Value -> {value} has to be one of types {possible_types}"
        self.__elements[element][key] = value

    
    def element(self, element):
        return self.__elements[element]

    def __str__(self):
        return "\n----------------\n".join([f"{key._name_} : {val}" for key, val in self.__elements.items()])
    
    def __getitem__(self, item):
        return self.__elements[item]
    
    def __repr__(self):
        return self.__str__()
    
    def save(self, path):
        import json
        with open(path, 'w') as fp:
            json.dump({str(key): self.__elements[key] for key in self.__elements}, fp)

    @staticmethod
    def load(path):
        import json 
        with open(path, 'r') as fp:
            theme = json.load(fp)   

        return Theme(**{key.lstrip("ThemeElement").lstrip("."): theme[key] for key in theme})