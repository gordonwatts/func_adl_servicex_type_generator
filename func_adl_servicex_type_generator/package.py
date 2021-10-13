from pathlib import Path
from typing import Any, Dict

import jinja2


def template_package_scaffolding(
    data: Dict[str, Any], template_path: Path, output_path: Path
):
    """Generate the package scaffolding:


    Args:
        data (Dict[str, Any]): Template replacement data needed for package
                               initialization
        template_path:         Location of our templates that we use to
                               generate the package
        output_path:           Location where we want to write the generated
                               package
    """
    # Load up the template structure and environment
    loader = jinja2.FileSystemLoader(str(template_path / "package"))
    env = jinja2.Environment(loader=loader)

    # Create the output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate the package
    for t in loader.list_templates():
        template = env.get_template(t)
        output_file = output_path / t
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("wt") as out:
            for line in template.render(data).splitlines():
                out.write(line)
                out.write("\n")

    # We rename the src directory to be the package name now
    assert (output_path / "src").exists()
    (output_path / "src").rename(output_path / data["package_name"])
