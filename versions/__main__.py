from entrypoint import entrypoint

from versions.main import versions

entrypoint(__name__).call(versions)
