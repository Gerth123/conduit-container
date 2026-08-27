"""
Patches Django 1.10's internals for Python 3.7+ compatibility.

Django 1.10 predates Python's __classcell__ propagation mechanism
(introduced in Python 3.7). Without these patches, Django's model
metaclass machinery raises RuntimeError on startup.

Applied automatically during the Docker build (see Dockerfile) so the
fix is reproducible and never requires manual editing of installed files.
"""
import sys
from pathlib import Path

site_packages = Path(sys.argv[1])

six_path = site_packages / "django" / "utils" / "six.py"
base_path = site_packages / "django" / "db" / "models" / "base.py"

six_content = six_path.read_text()

old_with_metaclass = '''def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})'''

new_with_metaclass = '''def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    class metaclass(type):

        def __new__(cls, name, this_bases, d):
            if sys.version_info[:2] >= (3, 7):
                resolved_bases = types.resolve_bases(bases)
                if resolved_bases is not bases:
                    d['__orig_bases__'] = bases
            else:
                resolved_bases = bases
            return meta(name, resolved_bases, d)

        @classmethod
        def __prepare__(cls, name, this_bases):
            return meta.__prepare__(name, bases)

    return type.__new__(metaclass, 'temporary_class', (), {})'''

if old_with_metaclass not in six_content:
    raise SystemExit("ERROR: with_metaclass block not found in six.py - Django version may have changed")

six_content = six_content.replace(old_with_metaclass, new_with_metaclass)

if "import types" not in six_content:
    six_content = six_content.replace("import sys", "import sys\nimport types", 1)

six_path.write_text(six_content)
print(f"Patched {six_path}")

base_content = base_path.read_text()

old_new_class_block = """        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})"""

new_new_class_block = """        module = attrs.pop('__module__')
        new_attrs = {'__module__': module}
        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        new_class = super_new(cls, name, bases, new_attrs)"""

if old_new_class_block not in base_content:
    raise SystemExit("ERROR: ModelBase.__new__ block not found in base.py - Django version may have changed")

base_content = base_content.replace(old_new_class_block, new_new_class_block)
base_path.write_text(base_content)
print(f"Patched {base_path}")