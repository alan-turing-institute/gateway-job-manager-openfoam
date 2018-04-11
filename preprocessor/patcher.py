"""
use Mako to apply patch to script
"""


from mako.template import Template as MakoTemplate



def patch(template_path, parameters, destination_path):
        """
        Method to apply a patch based on a supplied template file.
        """
        template = MakoTemplate(filename=template_path, input_encoding='utf-8')

        with open(destination_path, "w") as f:
            f.write(template.render(parameters=parameters))
