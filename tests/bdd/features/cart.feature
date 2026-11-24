Feature: Shopping cart
  As a shopper
  I want the cart to price what I add correctly
  So that I know what I will pay before I check out

  Background:
    Given I am on the home page

  Scenario Outline: Cart prices a product by its quantity
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    And I open the cart
    Then the cart contains "<product>"
    And the line price equals the unit price times <quantity>
    And the cart total equals the sum of the line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |
