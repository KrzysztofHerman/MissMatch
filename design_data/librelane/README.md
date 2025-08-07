# Decoder

To implement the decoder we use [LibreLane](https://github.com/librelane/librelane).

## Prerequisites

1. Install Nix according to the LibreLane docs: https://librelane.readthedocs.io/en/latest/getting_started/common/nix_installation/index.html
2. Use the `dev` branch of LibreLane: https://github.com/librelane/librelane/tree/dev

## Implementation

Enable an environment with the `dev` branch of LibreLane and run:

```
$ make
```

This will run the `decoder` Makefile target to build the decoder, and the `copy-final` target to copy the final directory of the latest run into the main folder.

To view the latest run using the OpenROAD GUI:

```
$ make view-openroad
```

To view the latest run using KLayout:

```
$ make view-klayout
```