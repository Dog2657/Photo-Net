from jinja2 import Environment, FileSystemLoader

environment = Environment(loader=FileSystemLoader("templates/"))

def render(templateName: str, **data):
    template = environment.get_template(templateName)
    return template.render(**data)