def pdb_to_xyz(pdb_file, xyz_file):
    atoms = []
    with open(pdb_file, 'r') as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                element = line[76:78].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                atoms.append((element, x, y, z))

    with open(xyz_file, 'w') as f:
        f.write(f"{len(atoms)}\n")
        f.write("Converted from PDB\n")
        for atom in atoms:
            f.write(f"{atom[0]:<2} {atom[1]:>12.6f} {atom[2]:>12.6f} {atom[3]:>12.6f}\n")

# Example usage
pdb_to_xyz("molecule.pdbx", "molecule.xyz")
