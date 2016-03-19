package(default_visibility = ["//visibility:private"])

load("//build/bzl:docker.bzl", "docker_pull")
load("@bazel_tools//tools/build_defs/docker:docker.bzl", "docker_build")
load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")

py_binary(
    name = "kube_addon_manager",
    srcs = [
        "kube_addon_manager.py",
        "util.py",
    ],
    deps = [
        "@bazel_tools//third_party/py/gflags",
    ],
)

py_test(
    name = "kube_addon_manager_test",
    srcs = [ "kube_addon_manager_test.py" ],
    deps = [ ":kube_addon_manager" ],
)
genrule(
    name = "kube_addon_manager_runfiles",
    tools = [ ":kube_addon_manager" ],
    outs = [ "kube_addon_manager_runfiles.tar" ],
    cmd = ""
    + "tar cfv $@ -C $$(dirname $(locations //kube_addon_manager:kube_addon_manager)) "
    + "kube_addon_manager.runfiles"
    ,
)

kubectl_url = "https://storage.googleapis.com/kubernetes-release/release/$${version}/bin/linux/amd64/kubectl"

genrule(
    name = "kubectl_bin",
    srcs = [ "kubectl.VERSION" ],
    outs = [ "kubectl" ],
    executable = 1,
    local = 1,
    cmd = ""
    + "version=$$(cat $(SRCS)); "
    + "curl --fail -sSL %s " % kubectl_url
    + "-o $@"
    ,
)

docker_pull(
    name = "python_slim",
    registry = "gcr.io",
    repository = "google_containers",
    image = "python",
    digest = "2.7.11-slim",
)

docker_build(
    name = "image",
    repository = "gcr.io/google_containers",
    base = ":python_slim",
    files = [
        ":kube_addon_manager",
        ":kubectl_bin",
    ],
    tars = [
        ":kube_addon_manager_runfiles",
    ],
    cmd = [ "python", "/kube_addon_manager" ],
    entrypoint = [ "/bin/sh", "-c" ],
)
