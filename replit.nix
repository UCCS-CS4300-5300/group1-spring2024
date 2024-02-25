{ pkgs }: {
  deps = [
    pkgs.google-cloud-sdk-gce
    pkgs.openssh_gssapi
  ];
}