{ pkgs }: {
  deps = [
     pkgs.geckodriver
    pkgs.google-cloud-sdk-gce
    pkgs.openssh_gssapi
  ];
}