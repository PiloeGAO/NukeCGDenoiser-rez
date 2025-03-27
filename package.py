name = "NukeCGDenoiser"

version = "1.0.0"

authors = ["mateuszwojt", "Leo Depoix"]

description = """
    OIDN node for Nuke.
    """

build_requires = [
    "cmake",
]

variants = [
    ["nuke-14"],
]

requires = [
    "IntelOpenImageDenoise-2.3.1"
]

uuid = "mateuszwojt.nukecgdenoiser"

build_command = "python {root}/build.py {install}"


def commands():
    env.NUKE_PATH.append("{root}/nuke")
