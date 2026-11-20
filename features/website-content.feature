Feature: Website Content
  As a blog author
  I want draft posts to be hidden from readers
  So that I can work on posts without publishing them

  Scenario: Draft post is not linked from the index
    Given the site has been built
    Then the index page should not contain a link to "/2026/02/07/draft.html"

  Scenario: Draft post is not linked from any published post
    Given the site has been built
    Then no published post should contain a link to "/2026/02/07/draft.html"

  Scenario: Draft post HTML is still generated for preview
    Given the site has been built
    Then the file "2026/02/07/draft.html" should exist in the output

  Scenario: Draft post has no navigation links to other posts
    Given the site has been built
    Then the page "2026/02/07/draft.html" should have no prev or next navigation links

  Scenario: Post pages are written to a yyyy/mm/dd path
    Given the site has been built
    Then the file "2026/02/15/on-static-sites.html" should exist in the output
    And the file "2026/02/07/hello-world.html" should exist in the output
    And the file "on-static-sites.html" should not exist in the output
    And the file "hello-world.html" should not exist in the output

  Scenario: Index links to posts by their dated path
    Given the site has been built
    Then the page "index.html" should link to "/2026/02/15/on-static-sites.html"
    And the page "index.html" should link to "/2026/02/07/hello-world.html"

  Scenario: Post navigation links use dated paths
    Given the site has been built
    Then the page "2026/02/15/on-static-sites.html" should link to "/2026/02/07/hello-world.html"
    And the page "2026/02/07/hello-world.html" should link to "/2026/02/15/on-static-sites.html"

  Scenario: Pages load the stylesheet from the site root
    Given the site has been built
    Then the page "index.html" should link to "/style.css"
    And the page "404.html" should link to "/style.css"
    And the page "2026/02/15/on-static-sites.html" should link to "/style.css"
