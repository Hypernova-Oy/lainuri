# Lainuri - open hardware library self-checkout device

## Dual license

- GPL-3 for all software
- TAPR Open Hardware License for everything else

## Open Source is Love

Buy from us at [Hypernova](https://www.hypernova.fi/lainuri-self-checkout-machine/)


## Deploying a new Lainuri to your library

### Place an order

- Choose your colour and engravings from [Cotter](https://cotter.co/materials/)

### Preparations in your Koha instance

- Prepare a separate user in Koha for each Lainuri. The Lainuri vendor needs to know the:
  - branchcode
  - username
  - password
  - your Koha-instance's URL

  The Lainuri-user needs the following permissions:
    - circulate -> circulate_remaining_permissions
    - borrowers -> view_borrowers
    - auth -> get_session
