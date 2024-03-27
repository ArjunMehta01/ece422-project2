import rsa

# Generate keys
(pubkey, privkey) = rsa.newkeys(512)

# Write public key to a file
with open('public_key.pem', 'wb') as f:
    f.write(pubkey.save_pkcs1())

# Write private key to a file
with open('private_key.pem', 'wb') as f:
    f.write(privkey.save_pkcs1())

print("Keys have been written to public_key.pem and private_key.pem")
