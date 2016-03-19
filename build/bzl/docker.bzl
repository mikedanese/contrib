load("@bazel_tools//tools/build_defs/docker:docker.bzl", "docker_build")

def docker_pull(name, image, digest, registry="index.docker.io", repository="library", visibility=["//visibility:public"]):
    args = [
        "--registry="+registry,
        "--repository="+repository,
        "--image="+image,
        "--digest="+digest,
        "--out_path=$@",
    ]
    cmd = ""
    for part in ["$(location //build/bzl:docker_pull)"] + args:
        cmd += part
        cmd += " "

    image_root = "%s_root" % name
    out_path = "%s.tar" % image_root

    native.genrule(
        name = image_root,
        outs = [out_path],
        cmd = cmd,
        message = "Pulling image '%s/%s/%s@%s'" % (registry, repository, image, digest),
        local = 1,
        tools = [
            "//build/bzl:docker_pull",
        ],
    )

    docker_build(
        name = name,
        tars = [ ":%s" % image_root ],
        visibility = visibility,
    )
