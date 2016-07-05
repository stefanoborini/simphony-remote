import tornado.options
from tornado.options import define, options

from traitlets import HasTraits, Int, Unicode

from remoteappmanager.utils import with_end_slash
from remoteappmanager.traitlets import set_traits_from_dict


class CommandLineConfig(HasTraits):
    """Configuration options for the application server"""

    # Options that are available for configuration at the command line,
    # and are set by jupyterhub
    user = Unicode(help="The user as specified at the jupyterhub login")

    ip = Unicode(help="The IP address to bind")

    port = Int(help="Port at which to spawn")

    cookie_name = Unicode(help="The cookie name for authentication")

    # This is the url path that the user sees and which leads to this server.
    # typically, it's /user/username
    base_url = Unicode(help="The base url where the server resides")

    # This is the host of the hub. It's always empty (jupyterhub decision)
    hub_host = Unicode(help="The url of the jupyterhub server")

    # This is a url path that sends the request to jupyterhub.
    # It's normally /hub/
    hub_prefix = Unicode(help="The url prefix of the jupyterhub")

    # This is a full url to reach the hub api (e.g. for authentication check)
    hub_api_url = Unicode(help="The url of the jupyterhub REST API")

    # The full URL where to access the reverse proxy API.
    proxy_api_url = Unicode(help="The url of the reverse proxy API")

    config_file = Unicode(help="The path of the configuration file")

    # Used to keep track if we already added the options
    # to the global config object. If that's the case, we skip the addition
    # to the command line global option object, or we will encounter a
    # redefinition error at define()
    command_line_options_inited = False

    def parse_config(self):
        """Parses the command line arguments, and assign their
        values to our local traits.
        """

        if not self.command_line_options_inited:
            for traitlet_name, traitlet in self.traits().items():
                    define(
                        traitlet_name,
                        default=traitlet.default_value,
                        type=type(traitlet.default_value),
                        help=traitlet.help)

        self.__class__.command_line_options_inited = True

        tornado.options.parse_command_line()

        set_traits_from_dict(self, options)

        # Normalize the base_url to end with a slash
        self.base_url = with_end_slash(self.base_url)
