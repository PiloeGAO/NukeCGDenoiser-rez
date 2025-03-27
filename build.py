import os
import os.path
import shutil
import sys
import subprocess
import platform


def get_os_information():
    """Get the os name and the architecture.

    Returns:
        tuple: OS name and architecture.
    """
    os_names = {
        "Windows": "windows",
        "Darwin": "macos",
    }
    architectures = {"AMD64": "x64", "arm64": "arm64"}
    os_platform = platform.system()
    os_architecture = platform.machine()

    return (
        os_names.get(os_platform, "linux"),
        architectures.get(os_architecture, "x64"),
    )


def build(source_path, build_path, install_path, targets):
    os_name, arch = get_os_information()

    build_directory = os.path.join(build_path, "build")

    def _build():
        src = os.path.join(source_path, "nuke")
        src_cpp = os.path.join(source_path, "src")
        dest = os.path.join(build_path, "nuke")

        if not os.path.exists(dest):
            shutil.copytree(src, dest)

        if os.path.isdir(build_directory):
            os.removedirs(build_directory)
        os.makedirs(build_directory)

        oidn_root = os.path.abspath(os.environ.get("OIDN_ROOT"))
        oidn_include_dir = os.path.join(oidn_root, "include")
        oidn_library = os.path.join(oidn_root, "lib", "OpenImageDenoise.lib")

        # Setup the build environment.
        setup_process = subprocess.Popen(
            [
                "cmake",
                "-G",
                "Visual Studio 16 2019",
                "-A",
                arch,
                f"-DOpenImageDenoise_INCLUDE_DIR={oidn_include_dir}",
                f"-DOpenImageDenoise_LIBRARY={oidn_library}",
                f"-DOIDN_ROOT={oidn_root}",
                src_cpp,
            ],
            cwd=build_directory,
        )

        try:
            _, _ = setup_process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            setup_process.kill()
            _, _ = setup_process.communicate()

        # Building the plugin.
        build_process = subprocess.Popen(
            [
                "cmake",
                "--build",
                build_directory,
                "--config",
                "Release",
            ],
            cwd=build_directory,
        )

        try:
            _, _ = build_process.communicate(timeout=999)
        except subprocess.TimeoutExpired:
            build_process.kill()
            _, _ = build_process.communicate()

    def _install():
        dest = os.path.join(install_path, "nuke")
        if os.path.exists(dest):
            shutil.rmtree(dest)


        shutil.copytree(
            os.path.join(build_path, "nuke"),
            dest
        )

        shutil.copy(
            os.path.join(
                build_directory,
                "src",
                "Release",
                "NukeDenoiser.dll"
            ),
            dest,
        )

    _build()

    if "install" in (targets or []):
        _install()


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
