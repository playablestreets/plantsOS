## patches.json
This file lists available patch folders and their metadata for the system to recognize and manage them.

### Structure
patches.json is an array of objects, each describing a patch. Each object can have the following fields:

- name (required): The name of the patch folder (must match a subfolder in this directory).
- git_url (optional): The URL to the patch's git repository.
- entrypoint (optional): The main Pure Data file to load for this patch (e.g., "main.pd").
- samplepack_url (optional): URL to download a sample pack associated with the patch.

### Example
```json
[
  {
    "name": "default",
    "git_url": "https://github.com/yourorg/default-patch.git",
    "entrypoint": "main.pd",
    "samplepack_url": "https://drive.google.com/uc?export=download&id=xxxx"
  },
  {
    "name": "custom",
    "git_url": "https://github.com/yourorg/custom-patch.git"
  }
]
```

## active_patch.txt
stores the currently active patch