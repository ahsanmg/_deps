# _deps

Place where I cook some big dependencies/packages/libraries from source, for my projects. Github Actions is free, so why not take advantage of this 🤷. It also gave me an excuse to learn more about Github Actions.

There are other ways of caching/reusing builds. But nothing meets the good old way of distributing packages. VCPKG/Conan are good for small packages but their caching mechanism doesn't help at all with bigger packages.

If you want to use it, feel free. You just fork it, go to the Actions Tab, click on a workflow, a Run Workflow button will appear in the workflow runs, click and enter the correct details to run it.

There's a `Main` workflow, which is responsible for creating the release tag and launching other reusable workflows depending on what you select to build. Currently,

1. ONNXRuntime Build maps to:
    * `Version\Tag\Branch` => `Version\Tag\Branch`
        * From the [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) repository.
    * `Features` => `Execution Providers`
        * Comma separated, correct options are `openvino`. More will be added.