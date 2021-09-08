import pytest

from jarvis.actions import action_registry
from jarvis.nlp.openai import openai_action_resolver as OR
from jarvis.nlp.openai import navigation

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2)


# NOTE: When openai model "temperature>0", these tests will occasionally fail
# as the model incorporates randomness.
@pytest.mark.parametrize(
    "question, expected",
    [
        (
            "log in to my wall street journal account",
            "ChangeURL `www.wsj.com` -> ClickLink `sign in`"
        ),
        (
            "goto shopify and create account",
            "ChangeURL `shopify.com` -> ClickLink `sign up`"
        ),
        (
            "open netflix and login",
            "ChangeURL `www.netflix.com` -> ClickLink `sign in`"
        ),
        (
            "open target and login",
            "ChangeURL `target.com` -> ClickLink `login`"
        ),
        (
            "goto tiktok website",
            "ChangeURL `tiktok.com`"
        ),
        (
            "open circleci select jarvis repo and click staging",
            "ChangeURL `circleci.com` -> ClickLink `repository` -> ClickLink `jarvis` -> ClickLink `staging`"
        )
    ]
)
def test_query_web_navigation_model(question, expected):
    answer = navigation.ask_web_navigation_model(question)
    print(answer)
    assert answer == expected


@pytest.mark.parametrize(
    "answer, expected",
    [
        (
            "ChangeURL `www.wsj.com` -> ClickLink `sign in`",
            [('ChangeURL', 'www.wsj.com'), ('ClickLink', 'sign in')]
        ),
        (
            "ChangeURL `amazon.com` -> FindSearchBar -> TypeText `ski mask` -> PressKey `enter`",
            [('ChangeURL', 'amazon.com'), ('FindSearchBar', None), ('TypeText', 'ski mask'), ("PressKey", "enter")]
        ),
        # (
        #     "ChangeURL `amazon.com` -> FindSearchBar -> ",  # Should raise exception but doesn't
        #     [('ChangeURL', 'amazon.com'), ('FindSearchBar', None)]
        # ),
        # (
        #     "ChangeURL `amazon.com` FindSearchBar -> ",  # Should raise exception but doesn't
        #     None,
        # )
        (
            "`amazon.com` 27862",
            None,  # Indicates raises exception
        ),
    ]
)
def testparse_answer_to_actions(answer, expected):
    if expected is None:
        with pytest.raises(Exception) as excinfo:
            print(excinfo)
            actions = OR.parse_answer_to_actions(answer)
    else:
        actions = OR.parse_answer_to_actions(answer)
        assert actions == expected


CMD = "log in to my wall street journal account"
ACTIONS = [('ChangeURL', 'www.wsj.com'), ('ClickLink', 'sign in')]
EXPECTED_CHAIN = {
        'name': 'log in to my wall street journal account',
        'phrases': ['log in to my wall street journal account'],
        'steps': [
            {
                'class_path': 'jarvis.automation.browser.browser_actions.ChangeURL',
                'params': {'url': 'www.wsj.com'}
            },
            {
                'class_path': 'jarvis.automation.browser.browser_actions.ClickLink',
                'params': {'link_text': 'sign in'}
            }
        ]
    }

def test_convert_actions_to_chain():
    cmd = CMD
    actions = ACTIONS
    expected = EXPECTED_CHAIN
    action_classes = action_registry.load_action_classes_from_modules("jarvis/automation")
    chain = OR.convert_actions_to_chain(
        cmd=cmd,
        actions=actions,
        action_classes=action_classes
    )
    pp.pprint(chain.to_dict())
    assert chain.to_dict() == expected


def test_infer_action_chain():
    cmd = CMD
    expected = EXPECTED_CHAIN
    action_classes = action_registry.load_action_classes_from_modules("jarvis/automation")
    chain = OR.infer_action_chain(cmd, action_classes)
    pp.pprint(chain.to_dict())
    assert chain.to_dict() == expected
