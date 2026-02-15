Feature: Website Content
  As a blog author
  I want draft posts to be hidden from readers
  So that I can work on posts without publishing them

  Scenario: Draft post is not linked from the index
    Given the site has been built
    Then the index page should not contain a link to "draft.html"

  Scenario: Draft post is not linked from any published post
    Given the site has been built
    Then no published post should contain a link to "draft.html"

  Scenario: Draft post HTML is still generated for preview
    Given the site has been built
    Then the file "draft.html" should exist in the output

  Scenario: Draft post has no navigation links to other posts
    Given the site has been built
    Then the page "draft.html" should have no prev or next navigation links
