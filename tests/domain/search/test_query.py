"""
Tests for search query module
"""

import pytest

from leedhunter.domain.search.query import (
    Query,
    QueryTerm,
    ExactPhrase,
    Operator,
    OperatorType,
    SiteOperator,
    IntitleOperator,
    InurlOperator,
    Exclusion,
    QueryBuilder,
)


class TestQueryTerm:
    """Tests for QueryTerm"""

    def test_create_term(self):
        """Test creating a QueryTerm"""
        term = QueryTerm(value="import")
        assert term.value == "import"
        assert term.normalized == "import"

    def test_term_normalization(self):
        """Test term normalization"""
        # Persian term
        term = QueryTerm(value="واردات")
        assert term.value == "واردات"
        assert term.normalized != ""  # Should be normalized

    def test_term_str(self):
        """Test term string representation"""
        term = QueryTerm(value="import")
        assert str(term) == "import"


class TestExactPhrase:
    """Tests for ExactPhrase"""

    def test_create_phrase(self):
        """Test creating an ExactPhrase"""
        phrase = ExactPhrase(value="واردات خودرو")
        assert phrase.value == "واردات خودرو"

    def test_phrase_str(self):
        """Test phrase string representation"""
        phrase = ExactPhrase(value="واردات خودرو")
        assert str(phrase) == '"واردات خودرو"'

    def test_phrase_normalization(self):
        """Test phrase normalization"""
        phrase = ExactPhrase(value="واردات خودرو")
        assert phrase.normalized != ""


class TestOperators:
    """Tests for operators"""

    def test_site_operator(self):
        """Test SiteOperator"""
        op = SiteOperator(domain="instagram.com")
        assert op.type == OperatorType.SITE
        assert op.value == "instagram.com"
        assert str(op) == "site:instagram.com"

    def test_intitle_operator(self):
        """Test IntitleOperator"""
        op = IntitleOperator(keyword="import")
        assert op.type == OperatorType.INTITLE
        assert op.value == "import"
        assert str(op) == "intitle:import"

    def test_inurl_operator(self):
        """Test InurlOperator"""
        op = InurlOperator(path="contact")
        assert op.type == OperatorType.INURL
        assert op.value == "contact"
        assert str(op) == "inurl:contact"

    def test_generic_operator(self):
        """Test generic Operator"""
        op = Operator(type=OperatorType.SITE, value="example.com")
        assert str(op) == "site:example.com"


class TestExclusion:
    """Tests for Exclusion"""

    def test_create_exclusion(self):
        """Test creating an Exclusion"""
        exclusion = Exclusion(value="used")
        assert exclusion.value == "used"
        assert exclusion.normalized == "used"

    def test_exclusion_str(self):
        """Test exclusion string representation"""
        exclusion = Exclusion(value="used")
        assert str(exclusion) == "-used"


class TestQuery:
    """Tests for Query"""

    def test_create_empty_query(self):
        """Test creating an empty query"""
        query = Query()
        assert query.is_empty()
        assert query.to_string() == ""

    def test_create_query_with_terms(self):
        """Test creating a query with terms"""
        query = Query(
            terms=[QueryTerm(value="import"), QueryTerm(value="cars")]
        )
        assert not query.is_empty()
        assert "import" in query.to_string()
        assert "cars" in query.to_string()

    def test_create_query_with_phrases(self):
        """Test creating a query with exact phrases"""
        query = Query(
            exact_phrases=[ExactPhrase(value="واردات خودرو")]
        )
        assert not query.is_empty()
        assert '"واردات خودرو"' in query.to_string()

    def test_create_query_with_operators(self):
        """Test creating a query with operators"""
        query = Query(
            operators=[SiteOperator(domain="instagram.com")]
        )
        assert not query.is_empty()
        assert "site:instagram.com" in query.to_string()

    def test_create_query_with_exclusions(self):
        """Test creating a query with exclusions"""
        query = Query(
            exclusions=[Exclusion(value="used")]
        )
        assert not query.is_empty()
        assert "-used" in query.to_string()

    def test_complex_query(self):
        """Test creating a complex query"""
        query = Query(
            terms=[QueryTerm(value="import")],
            exact_phrases=[ExactPhrase(value="واردات خودرو")],
            operators=[SiteOperator(domain="instagram.com")],
            exclusions=[Exclusion(value="used")],
        )
        query_str = query.to_string()
        assert "site:instagram.com" in query_str
        assert '"واردات خودرو"' in query_str
        assert "import" in query_str
        assert "-used" in query_str

    def test_get_normalized_terms(self):
        """Test getting normalized terms"""
        query = Query(
            terms=[QueryTerm(value="import")],
            exact_phrases=[ExactPhrase(value="test phrase")],
        )
        normalized = query.get_normalized_terms()
        assert len(normalized) == 2
        assert "import" in normalized

    def test_get_operators_by_type(self):
        """Test getting operators by type"""
        query = Query(
            operators=[
                SiteOperator(domain="instagram.com"),
                SiteOperator(domain="linkedin.com"),
                IntitleOperator(keyword="import"),
            ]
        )
        site_ops = query.get_operators_by_type(OperatorType.SITE)
        assert len(site_ops) == 2

    def test_has_site_operator(self):
        """Test checking for site operator"""
        query1 = Query(operators=[SiteOperator(domain="instagram.com")])
        assert query1.has_site_operator()

        query2 = Query(terms=[QueryTerm(value="test")])
        assert not query2.has_site_operator()

    def test_get_site_domain(self):
        """Test getting site domain"""
        query = Query(operators=[SiteOperator(domain="instagram.com")])
        assert query.get_site_domain() == "instagram.com"

    def test_validate_empty_query(self):
        """Test validating empty query"""
        query = Query()
        errors = query.validate()
        assert len(errors) > 0
        assert "empty" in errors[0].lower()

    def test_validate_valid_query(self):
        """Test validating valid query"""
        query = Query(terms=[QueryTerm(value="test")])
        errors = query.validate()
        assert len(errors) == 0
        assert query.is_valid()

    def test_validate_empty_term(self):
        """Test validating query with empty term"""
        # This should be caught by QueryTerm validation
        # but let's test the Query validation too
        query = Query(terms=[QueryTerm(value="test")])
        assert query.is_valid()

    def test_persian_query(self):
        """Test creating Persian queries"""
        query = Query(
            terms=[QueryTerm(value="واردات")],
            exact_phrases=[ExactPhrase(value="واردات خودرو")],
            operators=[SiteOperator(domain="instagram.com")],
        )
        query_str = query.to_string()
        assert "واردات" in query_str
        assert "site:instagram.com" in query_str

    def test_mixed_language_query(self):
        """Test creating mixed language queries"""
        query = Query(
            terms=[QueryTerm(value="import"), QueryTerm(value="واردات")],
            operators=[SiteOperator(domain="instagram.com")],
        )
        query_str = query.to_string()
        assert "import" in query_str
        assert "واردات" in query_str


class TestQueryBuilder:
    """Tests for QueryBuilder"""

    def test_build_empty_query(self):
        """Test building empty query"""
        query = QueryBuilder().build()
        assert query.is_empty()

    def test_build_with_terms(self):
        """Test building query with terms"""
        query = QueryBuilder().add_term("import").add_term("cars").build()
        assert len(query.terms) == 2
        assert not query.is_empty()

    def test_build_with_phrases(self):
        """Test building query with phrases"""
        query = QueryBuilder().add_exact_phrase("واردات خودرو").build()
        assert len(query.exact_phrases) == 1

    def test_build_with_site(self):
        """Test building query with site operator"""
        query = QueryBuilder().add_site("instagram.com").build()
        assert len(query.operators) == 1
        assert query.has_site_operator()

    def test_build_with_intitle(self):
        """Test building query with intitle operator"""
        query = QueryBuilder().add_intitle("import").build()
        assert len(query.operators) == 1

    def test_build_with_inurl(self):
        """Test building query with inurl operator"""
        query = QueryBuilder().add_inurl("contact").build()
        assert len(query.operators) == 1

    def test_build_with_exclusions(self):
        """Test building query with exclusions"""
        query = QueryBuilder().add_exclusion("used").build()
        assert len(query.exclusions) == 1

    def test_build_complex_query(self):
        """Test building complex query"""
        query = (
            QueryBuilder()
            .add_term("import")
            .add_exact_phrase("واردات خودرو")
            .add_site("instagram.com")
            .add_exclusion("used")
            .set_provider("google")
            .build()
        )
        assert len(query.terms) == 1
        assert len(query.exact_phrases) == 1
        assert len(query.operators) == 1
        assert len(query.exclusions) == 1
        assert query.provider == "google"

    def test_chaining(self):
        """Test method chaining"""
        builder = QueryBuilder()
        result = builder.add_term("test").add_site("example.com")
        assert result is builder

    def test_from_string_simple(self):
        """Test parsing simple query string"""
        query = QueryBuilder.from_string("import cars")
        assert len(query.terms) == 2

    def test_from_string_with_site(self):
        """Test parsing query string with site operator"""
        query = QueryBuilder.from_string("site:instagram.com import")
        assert query.has_site_operator()
        assert len(query.terms) == 1

    def test_from_string_with_phrase(self):
        """Test parsing query string with exact phrase"""
        query = QueryBuilder.from_string('"exact phrase" import')
        assert len(query.exact_phrases) == 1
        assert len(query.terms) == 1

    def test_from_string_with_exclusion(self):
        """Test parsing query string with exclusion"""
        query = QueryBuilder.from_string("import -used")
        assert len(query.terms) == 1
        assert len(query.exclusions) == 1

    def test_from_string_complex(self):
        """Test parsing complex query string"""
        query = QueryBuilder.from_string(
            'site:instagram.com "واردات خودرو" import -used'
        )
        assert query.has_site_operator()
        assert len(query.exact_phrases) == 1
        assert len(query.terms) == 1
        assert len(query.exclusions) == 1

    def test_fluent_api(self):
        """Test fluent API"""
        query = (
            QueryBuilder()
            .add_term("import")
            .add_exact_phrase("واردات خودرو")
            .add_site("instagram.com")
            .add_intitle("contact")
            .add_inurl("about")
            .add_exclusion("used")
            .build()
        )
        assert len(query.terms) == 1
        assert len(query.exact_phrases) == 1
        assert len(query.operators) == 3  # site, intitle, inurl
        assert len(query.exclusions) == 1
